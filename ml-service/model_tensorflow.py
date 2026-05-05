"""
TensorFlow Inference Module for HAM10000 Skin Disease Classification
Alternative to PyTorch model.py for inference using TensorFlow trained models
Includes Grad-CAM heatmap generation and confidence-based safety logic
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os
import json
import logging
import cv2
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Class labels for HAM10000 dataset (now includes 'unknown' class)
CLASS_LABELS = {
    'akiec': 'Actinic Keratosis/Intraepithelial Carcinoma',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'vasc': 'Vascular Lesions',
    'unknown': 'Non-Skin / Unknown'
}

# Confidence threshold - below this, return "Uncertain"
CONFIDENCE_THRESHOLD = 0.60

# Global model cache
_loaded_model = None
_loaded_model_path = None


def load_tensorflow_model(model_path="model_tensorflow.h5"):
    """
    Load TensorFlow model with caching
    
    Args:
        model_path: Path to the saved .h5 model file
    
    Returns:
        Loaded Keras model
    """
    global _loaded_model, _loaded_model_path
    
    # Return cached model if already loaded from same path
    if _loaded_model is not None and _loaded_model_path == model_path:
        logger.info(f"Using cached model from {model_path}")
        return _loaded_model
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    logger.info(f"Loading TensorFlow model from {model_path}...")
    try:
        model = tf.keras.models.load_model(model_path)
        _loaded_model = model
        _loaded_model_path = model_path
        logger.info(f"✓ Model loaded successfully")
        logger.info(f"  Input shape: {model.input_shape}")
        logger.info(f"  Output shape: {model.output_shape}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


def load_class_indices(class_indices_path="../backend/model/class_indices.json"):
    """Load class indices from JSON file"""
    try:
        if os.path.exists(class_indices_path):
            with open(class_indices_path, 'r') as f:
                class_to_idx = json.load(f)
            # Reverse to get idx to class mapping
            idx_to_class = {int(v): k for k, v in class_to_idx.items()}
            logger.info(f"Loaded {len(idx_to_class)} classes from JSON")
            return idx_to_class
    except Exception as e:
        logger.warning(f"Could not load class indices from JSON: {e}")
    
    # Fallback to hardcoded classes
    logger.info("Using fallback class mapping (7 classes)")
    return {i: cls for i, cls in enumerate(sorted(CLASS_LABELS.keys()))}


def preprocess_image(image_path, target_size=(224, 224)):
    """
    Load and preprocess image for TensorFlow model
    MUST MATCH EXACT PREPROCESSING FROM TRAINING
    
    Training preprocessing:
    1. load_img(target_size=(224, 224))
    2. img_to_array()
    3. Rescale: image / 255
    4. Add batch dimension
    
    Args:
        image_path: Path to the image file
        target_size: Target size for the image (MUST BE 224, 224)
    
    Returns:
        Preprocessed image as numpy array with shape (1, 224, 224, 3)
    """
    try:
        logger.info(f"Preprocessing image: {image_path}")
        
        # STEP 1: Load image with target size
        # This MUST match training's ImageDataGenerator.flow_from_directory
        img = load_img(image_path, target_size=target_size)
        logger.info(f"✓ Image loaded, size: {img.size}")
        
        # STEP 2: Convert to array
        # This MUST match training's img_to_array()
        img_array = img_to_array(img)
        logger.info(f"✓ Converted to array, shape: {img_array.shape}")
        logger.info(f"  Range before rescale: [{img_array.min():.1f}, {img_array.max():.1f}]")
        
        # STEP 3: Rescale to [0, 1]
        # This MUST match training's rescale=1./255
        img_array = img_array * (1./255)
        logger.info(f"✓ Rescaled by 1/255")
        logger.info(f"  Range after rescale: [{img_array.min():.4f}, {img_array.max():.4f}]")
        
        # STEP 4: Add batch dimension
        # Shape must be (1, 224, 224, 3) for model.predict()
        img_array = np.expand_dims(img_array, axis=0)
        logger.info(f"✓ Added batch dimension, shape: {img_array.shape}")
        
        return img_array
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise


def generate_gradcam_heatmap(model, img_array, original_image_path, class_index, last_conv_layer_name="conv5_block3_out"):
    """
    Generate Grad-CAM heatmap to visualize model predictions
    
    Args:
        model: Loaded Keras model
        img_array: Preprocessed image array (1, 224, 224, 3)
        original_image_path: Path to original image for overlay
        class_index: Index of the predicted class
        last_conv_layer_name: Name of last convolutional layer (ResNet50: conv5_block3_out)
    
    Returns:
        dict with heatmap image data or None if failed
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"GENERATING GRAD-CAM HEATMAP")
        logger.info(f"Predicted class index: {class_index}")
        logger.info(f"Last conv layer: {last_conv_layer_name}")
        
        # Build grad model
        try:
            last_conv_layer = model.get_layer(last_conv_layer_name)
            logger.info(f"✓ Found last conv layer: {last_conv_layer_name}")
        except:
            logger.warning(f"Could not find layer {last_conv_layer_name}, trying alternatives...")
            # Try to find last conv layer automatically
            last_conv_layer = None
            for layer in reversed(model.layers):
                if 'conv' in layer.name and len(layer.output_shape) == 4:
                    last_conv_layer = layer
                    last_conv_layer_name = layer.name
                    logger.info(f"✓ Found last conv layer: {last_conv_layer_name}")
                    break
            
            if last_conv_layer is None:
                logger.error("Could not find convolutional layer for Grad-CAM")
                return None
        
        # Create grad model
        grad_model = tf.keras.models.Model(
            [model.inputs],
            [last_conv_layer.output, model.output]
        )
        logger.info(f"✓ Grad model created")
        
        # Compute gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array, training=False)
            loss = predictions[:, class_index]
        
        grads = tape.gradient(loss, conv_outputs)
        
        if grads is None:
            logger.error("Gradient computation failed")
            return None
        
        logger.info(f"✓ Gradients computed")
        logger.info(f"  Conv output shape: {conv_outputs.shape}")
        logger.info(f"  Gradient shape: {grads.shape}")
        
        # Compute weights (average gradient across spatial dimensions)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        logger.info(f"✓ Pooled gradients computed, shape: {pooled_grads.shape}")
        
        # Generate heatmap
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Apply ReLU and normalize
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        heatmap = heatmap.numpy()
        
        logger.info(f"✓ Heatmap generated")
        logger.info(f"  Heatmap shape: {heatmap.shape}")
        logger.info(f"  Heatmap range: [{heatmap.min():.4f}, {heatmap.max():.4f}]")
        
        # Load original image
        original_img = cv2.imread(original_image_path)
        if original_img is None:
            logger.error(f"Could not load original image: {original_image_path}")
            return None
        
        original_height, original_width = original_img.shape[:2]
        logger.info(f"✓ Original image loaded: {original_width}x{original_height}")
        
        # Resize heatmap to original image size
        heatmap_resized = cv2.resize(heatmap, (original_width, original_height))
        heatmap_resized = np.uint8(255 * heatmap_resized)
        
        logger.info(f"✓ Heatmap resized to original dimensions")
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
        
        # Overlay on original image
        overlay = cv2.addWeighted(original_img, 0.6, heatmap_colored, 0.4, 0)
        
        # Convert to base64 for JSON serialization
        _, buffer = cv2.imencode('.jpg', overlay)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        logger.info(f"✓ Heatmap overlay created and encoded")
        logger.info(f"{'='*60}\n")
        
        return {
            "image": f"data:image/jpeg;base64,{img_base64}",
            "width": original_width,
            "height": original_height,
            "heatmap_shape": str(heatmap.shape)
        }
        
    except Exception as e:
        logger.error(f"Error generating Grad-CAM heatmap: {e}", exc_info=True)
        return None


def predict_image_tensorflow(image_path, top_k=3, generate_heatmap=True):
    """
    Predict skin disease from image using TensorFlow model with confidence safety logic
    
    Args:
        image_path: Path to the image file
        top_k: Number of top predictions to return
        generate_heatmap: Whether to generate Grad-CAM heatmap (True by default)
    
    Returns:
        dict with prediction, confidence, and optional heatmap:
        {
            "prediction": "Disease Name" or "Uncertain / Not a clear skin condition" or "No skin detected",
            "confidence": 0.85,
            "heatmap": {...} or None,
            "is_valid_skin": True/False,
            "is_confident": True/False,
            "top_k": [...],
            "debug_info": {...}
        }
    """
    
    logger.info(f"\n{'='*80}")
    logger.info(f"STEP 1: IMAGE RECEIVED (TensorFlow with Grad-CAM)")
    logger.info(f"Image path: {image_path}")
    logger.info(f"Generate heatmap: {generate_heatmap}")
    logger.info(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    
    # Validate image exists
    if not os.path.exists(image_path):
        logger.error(f"❌ Image not found: {image_path}")
        return {
            "error": "Image file not found",
            "image_path": image_path,
            "is_valid_skin": False,
            "is_confident": False,
            "heatmap": None
        }
    
    image_size = os.path.getsize(image_path)
    logger.info(f"✓ Image file exists, Size: {image_size} bytes")
    
    try:
        # Load class indices
        logger.info(f"\nSTEP 2: LOAD CLASS INDICES")
        idx_to_class = load_class_indices()
        num_classes = len(idx_to_class)
        logger.info(f"✓ Number of classes: {num_classes}")
        logger.info(f"✓ Class mapping: {idx_to_class}")
        
        # Load model
        logger.info(f"\nSTEP 3: LOAD TENSORFLOW MODEL")
        model = load_tensorflow_model("model_tensorflow.h5")
        
        # Preprocess image
        logger.info(f"\nSTEP 4: PREPROCESS IMAGE")
        img_array = preprocess_image(image_path)
        logger.info(f"✓ Image preprocessed, shape: {img_array.shape}")
        
        # Run inference
        logger.info(f"\nSTEP 5: RUN INFERENCE")
        predictions = model.predict(img_array, verbose=0)
        probs_np = predictions[0]  # Get first (and only) batch
        
        logger.info(f"✓ Predictions generated")
        logger.info(f"  Shape: {predictions.shape}")
        logger.info(f"  Sum: {probs_np.sum():.6f} (should be ≈1.0)")
        
        # Print raw predictions
        logger.info(f"\n=== RAW PREDICTIONS ===")
        for idx, prob in enumerate(probs_np):
            class_abbr = idx_to_class.get(int(idx), f"Unknown_{idx}")
            class_full = CLASS_LABELS.get(class_abbr, class_abbr)
            logger.info(f"  {idx}: {class_abbr:10} = {float(prob):.6f} ({float(prob)*100:.2f}%)")
        
        # Get top-K predictions
        logger.info(f"\nSTEP 6: EXTRACT TOP-K PREDICTIONS")
        top_indices = (-probs_np).argsort()[:top_k]
        top_probs = probs_np[top_indices]
        
        # Prepare top-K results
        top_k_results = []
        for idx, prob in zip(top_indices, top_probs):
            class_abbr = idx_to_class.get(int(idx), f"Unknown_{idx}")
            class_full = CLASS_LABELS.get(class_abbr, class_abbr)
            top_k_results.append({
                "label": class_abbr,
                "full_name": class_full,
                "confidence": round(float(prob), 4)
            })
        
        # Determine main prediction
        top_prob = float(top_probs[0])
        top_class_idx = int(top_indices[0])
        top_class_abbr = idx_to_class.get(top_class_idx, "unknown")
        top_class_full = CLASS_LABELS.get(top_class_abbr, top_class_abbr)
        
        logger.info(f"\nSTEP 7: APPLY SAFETY LOGIC")
        logger.info(f"Top prediction: {top_class_abbr}")
        logger.info(f"Top confidence: {top_prob:.4f}")
        logger.info(f"Threshold: {CONFIDENCE_THRESHOLD}")
        
        # SAFETY CHECK 1: Is it the "unknown" class?
        is_unknown = (top_class_abbr == "unknown")
        
        # SAFETY CHECK 2: Is confidence above threshold?
        is_confident = (top_prob >= CONFIDENCE_THRESHOLD)
        
        # Determine final prediction and validity
        is_valid_skin = False
        heatmap = None
        
        if is_unknown:
            logger.warning(f"⚠️ Predicted class is 'unknown' - rejecting prediction")
            prediction = "No skin detected or irrelevant image"
            prediction_full = "Non-Skin / Unknown"
            is_valid_skin = False
        elif not is_confident:
            logger.warning(f"⚠️ Confidence {top_prob:.4f} is below threshold {CONFIDENCE_THRESHOLD}")
            prediction = "Uncertain / Not a clear skin condition"
            prediction_full = "Uncertain"
            is_valid_skin = False
        else:
            logger.info(f"✓ Valid skin disease prediction with confidence {top_prob:.4f}")
            prediction = top_class_abbr
            prediction_full = top_class_full
            is_valid_skin = True
        
        # STEP 8: Generate Grad-CAM heatmap (only for valid predictions)
        logger.info(f"\nSTEP 8: GENERATE GRAD-CAM HEATMAP")
        if is_valid_skin and generate_heatmap:
            logger.info(f"Generating heatmap for class {top_class_abbr} (index {top_class_idx})...")
            heatmap = generate_gradcam_heatmap(model, img_array, image_path, top_class_idx)
            if heatmap:
                logger.info(f"✓ Heatmap generated successfully")
            else:
                logger.warning(f"⚠️ Heatmap generation failed, returning None")
        else:
            reason = "Not a valid skin prediction" if not is_valid_skin else "Heatmap generation disabled"
            logger.info(f"Skipping heatmap generation: {reason}")
        
        # Build response
        result = {
            "prediction": prediction,
            "prediction_full_name": prediction_full,
            "confidence": round(top_prob, 4),
            "is_valid_skin": is_valid_skin,
            "is_confident": is_confident,
            "heatmap": heatmap,
            "top_k": top_k_results,
            "warning": "This is an AI-assisted prediction and not a medical diagnosis. Always consult a healthcare professional.",
            "debug_info": {
                "model_type": "TensorFlow",
                "model_file": "model_tensorflow.h5",
                "image_path": image_path,
                "image_size": image_size,
                "model_classes": num_classes,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "top_prediction_raw": top_class_abbr,
                "is_unknown_class": is_unknown,
                "is_above_threshold": is_confident,
                "all_probabilities": {idx_to_class.get(i, f"Unknown_{i}"): float(probs_np[i]) 
                                     for i in range(num_classes)},
                "status": "✓ SUCCESS"
            }
        }
        
        logger.info(f"\n{'='*80}")
        logger.info(f"PREDICTION COMPLETE")
        logger.info(f"Prediction: {prediction}")
        logger.info(f"Full name: {prediction_full}")
        logger.info(f"Confidence: {top_prob:.4f}")
        logger.info(f"Is valid skin: {is_valid_skin}")
        logger.info(f"Has heatmap: {heatmap is not None}")
        logger.info(f"{'='*80}\n")
        
        return result
        
    except Exception as e:
        logger.error(f"\n{'='*80}")
        logger.error(f"❌ ERROR DURING PREDICTION")
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error(f"{'='*80}\n")
        return {
            "error": f"Prediction failed: {str(e)}",
            "is_valid_skin": False,
            "is_confident": False,
            "heatmap": None,
            "warning": "This is an AI-assisted prediction and not a medical diagnosis.",
            "debug_info": {
                "status": "❌ ERROR"
            }
        }


if __name__ == "__main__":
    # Test the inference
    test_image = "test_image.jpg"
    if os.path.exists(test_image):
        result = predict_image_tensorflow(test_image)
        print("Result:", json.dumps(result, indent=2))
    else:
        print(f"Test image not found: {test_image}")
