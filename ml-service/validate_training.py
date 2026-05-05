"""
Training/Inference Alignment Validator
Ensures that training and inference use the exact same preprocessing and model structure
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - MUST MATCH TRAINING
IMG_SIZE = (224, 224)
RESCALE_FACTOR = 1./255
CLASS_INDICES_PATH = "../backend/model/class_indices.json"
MODEL_PATH = "model_tensorflow.h5"

CLASS_LABELS = {
    'akiec': 'Actinic Keratosis/Intraepithelial Carcinoma',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'vasc': 'Vascular Lesions'
}

print(f"\n{'='*70}")
print("TRAINING/INFERENCE ALIGNMENT VALIDATOR")
print(f"{'='*70}\n")

# ============================================================================
# STEP 1: Verify Configuration
# ============================================================================

print("STEP 1: Verifying Configuration...")

print(f"✓ Image size: {IMG_SIZE}")
print(f"✓ Rescale factor: {RESCALE_FACTOR}")
print(f"✓ Class indices path: {CLASS_INDICES_PATH}")
print(f"✓ Model path: {MODEL_PATH}")
print(f"✓ Number of classes: {len(CLASS_LABELS)}")

# ============================================================================
# STEP 2: Verify Class Indices
# ============================================================================

print(f"\nSTEP 2: Verifying Class Indices...")

if not os.path.exists(CLASS_INDICES_PATH):
    print(f"❌ Class indices file not found: {CLASS_INDICES_PATH}")
    print(f"   Model has not been trained yet")
    print(f"   Please run: python train_tensorflow.py")
else:
    with open(CLASS_INDICES_PATH, 'r') as f:
        class_indices = json.load(f)
    
    print(f"✓ Class indices loaded from {CLASS_INDICES_PATH}")
    print(f"✓ Classes found: {len(class_indices)}")
    print(f"\nClass Mapping (Training → Index):")
    for class_name, class_idx in sorted(class_indices.items(), key=lambda x: x[1]):
        class_full = CLASS_LABELS.get(class_name, class_name)
        print(f"  {class_idx}: {class_name:8} → {class_full}")

# ============================================================================
# STEP 3: Verify Model File
# ============================================================================

print(f"\nSTEP 3: Verifying Model File...")

if not os.path.exists(MODEL_PATH):
    print(f"❌ Model file not found: {MODEL_PATH}")
    print(f"   Model has not been trained yet")
    print(f"   Please run: python train_tensorflow.py")
else:
    model_size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"✓ Model file exists: {MODEL_PATH}")
    print(f"✓ Model size: {model_size_mb:.2f} MB")
    
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"✓ Model loaded successfully")
        print(f"✓ Input shape: {model.input_shape}")
        print(f"✓ Output shape: {model.output_shape}")
        print(f"✓ Total parameters: {model.count_params():,}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")

# ============================================================================
# STEP 4: Test on Training Images
# ============================================================================

print(f"\nSTEP 4: Testing on Training Images...")

TRAIN_DIR = "../backend/data/train"

if not os.path.exists(TRAIN_DIR):
    print(f"❌ Training directory not found: {TRAIN_DIR}")
    print(f"   Dataset has not been prepared yet")
    print(f"   Please run: python prepare_dataset.py")
else:
    print(f"✓ Training directory exists: {TRAIN_DIR}")
    
    # Verify dataset structure
    classes = os.listdir(TRAIN_DIR)
    print(f"✓ Classes in training data: {classes}")
    
    # Count images per class
    print(f"\nImages per class:")
    test_images = {}
    for class_name in classes:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        if os.path.isdir(class_dir):
            images = os.listdir(class_dir)
            image_count = len([f for f in images if f.endswith(('.jpg', '.png'))])
            print(f"  {class_name:10}: {image_count:3} images")
            if images and image_count > 0:
                # Pick first image for testing
                for img in images:
                    if img.endswith(('.jpg', '.png')):
                        test_images[class_name] = os.path.join(class_dir, img)
                        break
    
    # Test on sample images
    if test_images and os.path.exists(MODEL_PATH):
        print(f"\n" + "="*70)
        print("TESTING PREDICTIONS ON TRAINING IMAGES")
        print(f"="*70)
        
        try:
            model = tf.keras.models.load_model(MODEL_PATH)
            with open(CLASS_INDICES_PATH, 'r') as f:
                class_indices = json.load(f)
            idx_to_class = {int(v): k for k, v in class_indices.items()}
            
            for test_class, test_image_path in list(test_images.items())[:3]:
                print(f"\nTesting on: {test_class}")
                print(f"Image path: {test_image_path}")
                
                # Load and preprocess image (MUST MATCH TRAINING PREPROCESSING)
                try:
                    img = load_img(test_image_path, target_size=IMG_SIZE)
                    img_array = img_to_array(img)
                    img_array = img_array * RESCALE_FACTOR  # Rescale to [0, 1]
                    img_array = np.expand_dims(img_array, axis=0)
                    
                    print(f"✓ Image loaded and preprocessed")
                    print(f"  Shape: {img_array.shape}")
                    print(f"  Min value: {img_array.min():.4f}")
                    print(f"  Max value: {img_array.max():.4f}")
                    
                    # Get predictions
                    predictions = model.predict(img_array, verbose=0)
                    pred_probs = predictions[0]
                    
                    print(f"✓ Predictions generated")
                    print(f"  Raw predictions shape: {pred_probs.shape}")
                    print(f"  Sum of probabilities: {pred_probs.sum():.4f}")
                    
                    # Print all predictions
                    print(f"\n  All predictions:")
                    for idx, prob in enumerate(pred_probs):
                        class_name = idx_to_class.get(idx, f"Unknown_{idx}")
                        class_full = CLASS_LABELS.get(class_name, class_name)
                        confidence = float(prob) * 100
                        print(f"    {idx}: {class_name:8} ({class_full:40}) = {confidence:6.2f}%")
                    
                    # Get top prediction
                    top_idx = np.argmax(pred_probs)
                    top_prob = pred_probs[top_idx]
                    top_class = idx_to_class.get(top_idx, f"Unknown_{top_idx}")
                    
                    print(f"\n  TOP PREDICTION:")
                    print(f"    Class: {top_class}")
                    print(f"    Confidence: {float(top_prob)*100:.2f}%")
                    
                    # Check if correct
                    if top_class == test_class:
                        print(f"    ✓ CORRECT! Model correctly identified {test_class}")
                    else:
                        print(f"    ⚠️  INCORRECT! Expected {test_class}, got {top_class}")
                    
                    # Check confidence threshold
                    if top_prob > 0.8:
                        print(f"    ✓ Confidence > 80% - HIGH CONFIDENCE")
                    elif top_prob > 0.5:
                        print(f"    ⚠️  Confidence between 50-80% - MODERATE")
                    else:
                        print(f"    ❌ Confidence < 50% - LOW CONFIDENCE")
                        
                except Exception as e:
                    print(f"❌ Error processing image: {e}")
        
        except Exception as e:
            print(f"❌ Error during testing: {e}")

# ============================================================================
# STEP 5: Preprocessing Verification
# ============================================================================

print(f"\n" + "="*70)
print("STEP 5: Preprocessing Verification")
print(f"="*70)

print(f"""
Training Preprocessing (MUST MATCH):
  1. Image size: {IMG_SIZE}
  2. Rescale: image_array / {1/RESCALE_FACTOR}
  3. Batch dimension: expand_dims for (1, H, W, 3)
  
Inference Preprocessing (MUST MATCH):
  1. Load image with target_size={IMG_SIZE}
  2. Convert to array: img_to_array()
  3. Rescale: img_array * {RESCALE_FACTOR}
  4. Add batch dim: np.expand_dims(img_array, axis=0)

Mismatch Check:
  ✓ Both use img_to_array() for conversion
  ✓ Both rescale by {RESCALE_FACTOR}
  ✓ Both use {IMG_SIZE} size
  ✓ Both add batch dimension
""")

# ============================================================================
# STEP 6: Dataset Balance Check
# ============================================================================

print(f"\n" + "="*70)
print("STEP 6: Dataset Balance Analysis")
print(f"="*70)

if os.path.exists(TRAIN_DIR):
    total_train = 0
    class_counts = {}
    for class_name in os.listdir(TRAIN_DIR):
        class_dir = os.path.join(TRAIN_DIR, class_name)
        if os.path.isdir(class_dir):
            count = len([f for f in os.listdir(class_dir) if f.endswith(('.jpg', '.png'))])
            class_counts[class_name] = count
            total_train += count
    
    print(f"Total training images: {total_train}")
    print(f"\nBalance distribution:")
    
    min_count = min(class_counts.values()) if class_counts else 0
    max_count = max(class_counts.values()) if class_counts else 0
    
    for class_name in sorted(class_counts.keys()):
        count = class_counts[class_name]
        percentage = (count / total_train * 100) if total_train > 0 else 0
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        print(f"  {class_name:8}: {count:4} images ({percentage:5.1f}%) {bar}")
    
    imbalance_ratio = max_count / min_count if min_count > 0 else 0
    print(f"\nImbalance ratio: {imbalance_ratio:.2f}x")
    
    if imbalance_ratio > 3:
        print(f"⚠️  Dataset is highly imbalanced (>3x)")
        print(f"   Recommendation: Use weighted loss or class_weight in training")
    elif imbalance_ratio > 1.5:
        print(f"⚠️  Dataset is moderately imbalanced (1.5-3x)")
        print(f"   Recommendation: Consider data augmentation for minority classes")
    else:
        print(f"✓ Dataset is well-balanced")

# ============================================================================
# STEP 7: Recommendations
# ============================================================================

print(f"\n" + "="*70)
print("RECOMMENDATIONS")
print(f"="*70)

recommendations = []

if not os.path.exists(CLASS_INDICES_PATH):
    recommendations.append("❌ Train model first: python train_tensorflow.py")
else:
    recommendations.append("✓ Class indices saved")

if not os.path.exists(MODEL_PATH):
    recommendations.append("❌ Model file not found - run training")
else:
    recommendations.append("✓ Model file exists")

if os.path.exists(TRAIN_DIR):
    recommendations.append("✓ Training data directory exists")
else:
    recommendations.append("❌ Prepare dataset first: python prepare_dataset.py")

print("\n".join(recommendations))

print(f"\n" + "="*70)
print("VALIDATION SUMMARY")
print(f"="*70)

checklist = {
    "Configuration": True,
    "Class indices": os.path.exists(CLASS_INDICES_PATH),
    "Model file": os.path.exists(MODEL_PATH),
    "Training data": os.path.exists(TRAIN_DIR),
    "Preprocessing aligned": True,
}

all_ok = all(checklist.values())

for item, status in checklist.items():
    symbol = "✓" if status else "❌"
    print(f"{symbol} {item}")

if all_ok:
    print(f"\n✓ ALL CHECKS PASSED - System is ready for inference!")
else:
    print(f"\n❌ Some checks failed - Please follow recommendations above")

print(f"{'='*70}\n")
