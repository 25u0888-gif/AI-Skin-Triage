import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import json
import logging
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Class labels for HAM10000 dataset
CLASS_LABELS = {
    'akiec': 'Actinic Keratosis/Intraepithelial Carcinoma',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'vasc': 'Vascular Lesions'
}

def get_model(num_classes=7):
    """Create ResNet18 model with specified number of output classes"""
    model = models.resnet18(weights=None)
    # Modify final layer for multi-class classification
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

def load_class_indices():
    """Load class indices from JSON file"""
    try:
        class_indices_path = "../backend/model/class_indices.json"
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

def predict_image(image_path, top_k=3, confidence_threshold=0.6):
    """
    Predict skin disease from image with top-K predictions and confidence threshold
    
    Args:
        image_path: Path to the image file
        top_k: Number of top predictions to return
        confidence_threshold: Minimum confidence threshold (0.0-1.0)
    
    Returns:
        dict with structure:
        {
            "prediction": "Disease Name",
            "confidence": 0.85,
            "top_k": [
                {"label": "Disease 1", "confidence": 0.85},
                {"label": "Disease 2", "confidence": 0.10},
                {"label": "Disease 3", "confidence": 0.05}
            ],
            "warning": "This is an AI-assisted prediction and not a medical diagnosis.",
            "debug_info": {...}
        }
    """
    
    logger.info(f"\n{'='*60}")
    logger.info(f"STEP 1: IMAGE RECEIVED")
    logger.info(f"Image path: {image_path}")
    
    # Validate image exists
    if not os.path.exists(image_path):
        logger.error(f"❌ Image not found: {image_path}")
        return {
            "error": "Image file not found",
            "image_path": image_path
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
        
        # Check if model file exists
        logger.info(f"\nSTEP 3: CHECK MODEL FILE")
        model_path = "model.pth"
        model_exists = os.path.exists(model_path)
        model_size = os.path.getsize(model_path) if model_exists else 0
        logger.info(f"Model file: {model_path}")
        logger.info(f"Model exists: {model_exists}, Size: {model_size} bytes")
        
        if not model_exists or model_size == 0:
            logger.warning(f"⚠️  Model file missing or empty! Size: {model_size} bytes")
            logger.warning(f"Using random predictions as fallback for testing")
            
            # Create random but realistic predictions for testing
            probs_np = np.random.dirichlet(np.ones(num_classes)) * 0.95
            probs_np += np.random.uniform(0.01, 0.03, num_classes)
            probs_np = probs_np / probs_np.sum()  # Normalize to sum to 1
            
            logger.info(f"Generated random predictions: {probs_np}")
            
            # Get top-K predictions
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
            
            # Log all predictions for debugging
            logger.info("=== ALL PREDICTIONS (FALLBACK) ===")
            for i in range(num_classes):
                class_abbr = idx_to_class.get(i, f"Unknown_{i}")
                class_full = CLASS_LABELS.get(class_abbr, class_abbr)
                logger.info(f"{i}: {class_abbr} ({class_full}): {probs_np[i]:.4f}")
            
            # Use top prediction
            top_prob = float(top_probs[0])
            top_class_abbr = idx_to_class.get(int(top_indices[0]), "Unknown")
            top_class_full = CLASS_LABELS.get(top_class_abbr, top_class_abbr)
            
            result = {
                "prediction": top_class_abbr,
                "prediction_full_name": top_class_full,
                "confidence": round(top_prob, 4),
                "top_k": top_k_results,
                "warning": "⚠️ FALLBACK MODE: Model file not found. Using random predictions for demonstration. This is NOT a real medical diagnosis. Always consult a healthcare professional.",
                "debug_info": {
                    "model_file": model_path,
                    "model_status": "MISSING - Using fallback",
                    "image_path": image_path,
                    "image_size": image_size,
                    "model_classes": num_classes,
                    "confidence_threshold": confidence_threshold,
                    "predictions_logged": True
                }
            }
            
            logger.info(f"Returning fallback prediction: {top_class_abbr} ({top_prob:.4f})")
            return result
        
        # Load actual model
        logger.info(f"\nSTEP 3: LOAD MODEL")
        model = get_model(num_classes=num_classes)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        logger.info(f"✓ Model loaded successfully from {model_path}")
        
        # Print model summary on first load
        logger.info("=== MODEL SUMMARY ===")
        logger.info(str(model))
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"Total parameters: {total_params:,}")
        
        # Image preprocessing
        logger.info(f"\nSTEP 4: PREPROCESS IMAGE")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        image = Image.open(image_path).convert("RGB")
        original_size = image.size
        image_tensor = transform(image).unsqueeze(0)
        logger.info(f"✓ Original image size: {original_size}")
        logger.info(f"✓ Processed tensor shape: {image_tensor.shape}")
        
        # Inference
        logger.info(f"\nSTEP 5: RUN INFERENCE")
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        logger.info(f"✓ Raw outputs shape: {outputs.shape}")
        logger.info(f"✓ Softmax applied, outputs shape: {probabilities.shape}")
        
        # Convert to numpy for easier handling
        probs_np = probabilities.cpu().numpy()
        
        # Get top-K predictions
        top_indices = (-probs_np).argsort()[:top_k]
        top_probs = probs_np[top_indices]
        
        logger.info(f"\nSTEP 6: EXTRACT PREDICTIONS")
        
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
        
        # Log all predictions for debugging
        logger.info("=== ALL PREDICTIONS ===")
        for i in range(num_classes):
            class_abbr = idx_to_class.get(i, f"Unknown_{i}")
            class_full = CLASS_LABELS.get(class_abbr, class_abbr)
            logger.info(f"{i}: {class_abbr} ({class_full}): {probs_np[i]:.4f}")
        
        # Determine main prediction
        top_prob = float(top_probs[0])
        top_class_abbr = idx_to_class.get(int(top_indices[0]), "Unknown")
        top_class_full = CLASS_LABELS.get(top_class_abbr, top_class_abbr)
        
        logger.info(f"\nSTEP 7: DETERMINE CONFIDENCE")
        logger.info(f"Top prediction confidence: {top_prob:.4f}")
        logger.info(f"Confidence threshold: {confidence_threshold}")
        
        # Check confidence threshold
        if top_prob < confidence_threshold:
            prediction = "Uncertain - Low Confidence"
            logger.warning(f"⚠️ Confidence {top_prob:.4f} is below threshold {confidence_threshold}")
        else:
            prediction = top_class_abbr
            logger.info(f"✓ Confidence above threshold, using prediction: {prediction}")
        
        result = {
            "prediction": prediction,
            "prediction_full_name": top_class_full if prediction != "Uncertain - Low Confidence" else "Uncertain",
            "confidence": round(top_prob, 4),
            "top_k": top_k_results,
            "warning": "This is an AI-assisted prediction and not a medical diagnosis. Always consult a healthcare professional.",
            "debug_info": {
                "model_file": model_path,
                "image_path": image_path,
                "image_size": original_size,
                "model_classes": num_classes,
                "confidence_threshold": confidence_threshold,
                "predictions_logged": True,
                "status": "✓ SUCCESS"
            }
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"PREDICTION COMPLETE")
        logger.info(f"Prediction: {prediction}")
        logger.info(f"Full name: {result['prediction_full_name']}")
        logger.info(f"Confidence: {top_prob:.4f}")
        logger.info(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ ERROR DURING PREDICTION")
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error(f"{'='*60}\n")
        return {
            "error": f"Prediction failed: {str(e)}",
            "warning": "This is an AI-assisted prediction and not a medical diagnosis."
        }
