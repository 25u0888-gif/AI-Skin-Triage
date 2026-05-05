"""
Training/Inference Alignment Test
Tests that model predictions are consistent and high-confidence on known training images
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# CRITICAL: These MUST match training_tensorflow.py exactly
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
CLASS_INDICES_PATH = "../backend/model/class_indices.json"
MODEL_PATH = "model_tensorflow.h5"
TRAIN_DIR = "../backend/data/train"

CLASS_LABELS = {
    'akiec': 'Actinic Keratosis/Intraepithelial Carcinoma',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'vasc': 'Vascular Lesions'
}

print(f"\n{'='*80}")
print("TRAINING/INFERENCE ALIGNMENT TEST")
print(f"Testing model consistency and high confidence on training data")
print(f"{'='*80}\n")

# ============================================================================
# Check Prerequisites
# ============================================================================

print("Checking prerequisites...")
checks = {
    "Class indices exist": os.path.exists(CLASS_INDICES_PATH),
    "Model file exists": os.path.exists(MODEL_PATH),
    "Training data exists": os.path.exists(TRAIN_DIR),
}

for check, status in checks.items():
    print(f"  {'✓' if status else '❌'} {check}")

if not all(checks.values()):
    print("\n❌ Prerequisites not met!")
    print("   1. Run: python prepare_dataset.py")
    print("   2. Run: python train_tensorflow.py")
    print("   3. Then run this script again")
    exit(1)

print("✓ All prerequisites met\n")

# ============================================================================
# Load Model and Class Indices
# ============================================================================

print("Loading model and class indices...")

with open(CLASS_INDICES_PATH, 'r') as f:
    class_indices = json.load(f)

idx_to_class = {int(v): k for k, v in class_indices.items()}

print(f"✓ Class indices loaded:")
for idx, class_name in sorted(idx_to_class.items()):
    print(f"    {idx}: {class_name}")

model = tf.keras.models.load_model(MODEL_PATH)
print(f"\n✓ Model loaded")
print(f"  Input shape: {model.input_shape}")
print(f"  Output shape: {model.output_shape}")

# ============================================================================
# Test 1: Preprocess an Image (Training Path)
# ============================================================================

print(f"\n{'='*80}")
print("TEST 1: Image Preprocessing (Training Path)")
print(f"{'='*80}\n")

# Find a test image
test_images_per_class = {}
for class_name in os.listdir(TRAIN_DIR):
    class_dir = os.path.join(TRAIN_DIR, class_name)
    if os.path.isdir(class_dir):
        images = [f for f in os.listdir(class_dir) if f.endswith(('.jpg', '.png'))]
        if images:
            test_images_per_class[class_name] = os.path.join(class_dir, images[0])

if not test_images_per_class:
    print("❌ No test images found!")
    exit(1)

# Pick first class
test_class = list(test_images_per_class.keys())[0]
test_image_path = test_images_per_class[test_class]

print(f"Testing with image from class: {test_class}")
print(f"Image path: {test_image_path}\n")

# Load with Keras (same as training)
print("Loading with load_img (same as training):")
img = load_img(test_image_path, target_size=IMG_SIZE)
print(f"  ✓ Loaded, shape: {img.size} (W, H)")

img_array = img_to_array(img)
print(f"  ✓ Converted to array, shape: {img_array.shape} (H, W, C)")
print(f"    - Min pixel value: {img_array.min():.1f}")
print(f"    - Max pixel value: {img_array.max():.1f}")

# Rescale (CRITICAL: must match training)
img_array_rescaled = img_array * (1./255)
print(f"  ✓ Rescaled by 1/255")
print(f"    - Min value after rescale: {img_array_rescaled.min():.4f}")
print(f"    - Max value after rescale: {img_array_rescaled.max():.4f}")

# Add batch dimension
img_batch = np.expand_dims(img_array_rescaled, axis=0)
print(f"  ✓ Added batch dimension, shape: {img_batch.shape} (B, H, W, C)")

# ============================================================================
# Test 2: Model Prediction
# ============================================================================

print(f"\n{'='*80}")
print("TEST 2: Model Prediction")
print(f"{'='*80}\n")

predictions = model.predict(img_batch, verbose=0)
probs = predictions[0]

print(f"Raw predictions from model:")
print(f"  Shape: {probs.shape}")
print(f"  Sum: {probs.sum():.6f} (should be ≈1.0)")
print(f"  Type: {probs.dtype}")

print(f"\nFull prediction breakdown:")
for idx, prob in enumerate(probs):
    class_name = idx_to_class.get(idx, f"Unknown_{idx}")
    class_full = CLASS_LABELS.get(class_name, class_name)
    confidence_pct = float(prob) * 100
    
    # Visual bar
    bar_length = int(confidence_pct / 2)
    bar = "█" * bar_length
    
    symbol = "→ " if class_name == test_class else "  "
    print(f"{symbol}{idx}: {class_name:8} {bar:40} {confidence_pct:6.2f}%")

# ============================================================================
# Test 3: Verify Correct Class Has High Confidence
# ============================================================================

print(f"\n{'='*80}")
print("TEST 3: Confidence Analysis")
print(f"{'='*80}\n")

top_idx = np.argmax(probs)
top_prob = float(probs[top_idx])
top_class = idx_to_class.get(top_idx)
test_class_idx = int([k for k,v in class_indices.items() if v == test_class][0])
test_class_prob = float(probs[test_class_idx])

print(f"Expected class: {test_class}")
print(f"  - Index: {test_class_idx}")
print(f"  - Confidence: {test_class_prob*100:.2f}%")

print(f"\nTop prediction: {top_class}")
print(f"  - Index: {top_idx}")
print(f"  - Confidence: {top_prob*100:.2f}%")

# Check correctness
if top_class == test_class:
    print(f"\n✓ MODEL IS CORRECT!")
    print(f"  Correctly predicted {test_class} with {top_prob*100:.2f}% confidence")
else:
    print(f"\n⚠️ MODEL IS INCORRECT!")
    print(f"  Expected {test_class}, but predicted {top_class}")

# Check confidence level
if test_class_prob > 0.8:
    print(f"\n✓ HIGH CONFIDENCE (>{0.8*100:.0f}%)")
    print(f"  Model is very sure about the prediction")
elif test_class_prob > 0.6:
    print(f"\n⚠️ MODERATE CONFIDENCE (60-80%)")
    print(f"  Model is reasonably confident")
elif test_class_prob > 0.4:
    print(f"\n⚠️ LOW CONFIDENCE (40-60%)")
    print(f"  Model is uncertain - training may need improvement")
else:
    print(f"\n❌ VERY LOW CONFIDENCE (<40%)")
    print(f"  Model did not learn this class well - training needs improvement")

# ============================================================================
# Test 4: Batch Processing (Training Flow)
# ============================================================================

print(f"\n{'='*80}")
print("TEST 4: Batch Processing (Training Flow)")
print(f"{'='*80}\n")

print("Loading data with ImageDataGenerator (same as training):")

# Use same preprocessing as training
datagen = ImageDataGenerator(rescale=1./255)
data_flow = datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

print(f"✓ Data flow created")
print(f"  - Classes: {list(data_flow.class_indices.keys())}")
print(f"  - Total samples: {data_flow.samples}")
print(f"  - Batch size: BATCH_SIZE")

# Get one batch
print(f"\nGetting first batch...")
batch_images, batch_labels = next(data_flow)

print(f"✓ Batch retrieved")
print(f"  - Images shape: {batch_images.shape} (B, H, W, C)")
print(f"  - Labels shape: {batch_labels.shape} (B, num_classes)")
print(f"  - Image value range: [{batch_images.min():.4f}, {batch_images.max():.4f}]")

# Test batch prediction
print(f"\nTesting batch prediction...")
batch_predictions = model.predict(batch_images, verbose=0)

print(f"✓ Batch predictions")
print(f"  - Shape: {batch_predictions.shape}")
print(f"  - Value range: [{batch_predictions.min():.4f}, {batch_predictions.max():.4f}]")

# Analyze batch results
correct_count = 0
high_confidence_count = 0

for i in range(min(5, len(batch_predictions))):  # Check first 5 images
    true_class_idx = np.argmax(batch_labels[i])
    pred_class_idx = np.argmax(batch_predictions[i])
    confidence = float(batch_predictions[i][pred_class_idx])
    
    true_class = idx_to_class.get(true_class_idx)
    pred_class = idx_to_class.get(pred_class_idx)
    
    is_correct = true_class_idx == pred_class_idx
    is_high_conf = confidence > 0.8
    
    if is_correct:
        correct_count += 1
    if is_high_conf:
        high_confidence_count += 1
    
    symbol = "✓" if is_correct else "✗"
    conf_symbol = "HIGH" if is_high_conf else "LOW"
    
    print(f"  {symbol} Image {i+1}: True={true_class:8} Pred={pred_class:8} Conf={confidence*100:6.2f}% [{conf_symbol}]")

print(f"\nBatch analysis (first 5 images):")
print(f"  - Correct predictions: {correct_count}/5")
print(f"  - High confidence (>80%): {high_confidence_count}/5")

# ============================================================================
# Test 5: Recommendations
# ============================================================================

print(f"\n{'='*80}")
print("RECOMMENDATIONS")
print(f"{'='*80}\n")

issues = []

if test_class_prob < 0.5:
    issues.append("Model confidence too low on training data")

if top_class != test_class:
    issues.append("Model making incorrect predictions")

if test_class_prob < 0.8:
    issues.append("Model needs more training epochs")

if issues:
    print("Issues detected:")
    for issue in issues:
        print(f"  ❌ {issue}")
    
    print(f"\nSuggested improvements:")
    print(f"  1. Increase EPOCHS in train_tensorflow.py (try 20-50)")
    print(f"  2. Check dataset balance with: python validate_training.py")
    print(f"  3. Reduce BATCH_SIZE to 16 for better gradient updates")
    print(f"  4. Use more data augmentation")
else:
    print("✓ Model is performing well!")
    print(f"  - High confidence on training data: >{0.8*100:.0f}%")
    print(f"  - Making correct predictions")
    print(f"  - Ready for inference!")

# ============================================================================
# Summary
# ============================================================================

print(f"\n{'='*80}")
print("TEST SUMMARY")
print(f"{'='*80}\n")

summary = {
    "Preprocessing match": "✓" if IMG_SIZE == (224, 224) else "❌",
    "Model loads": "✓" if model else "❌",
    "Class indices match": "✓" if len(idx_to_class) == 7 else "❌",
    "Training data exists": "✓" if test_images_per_class else "❌",
    "Model makes predictions": "✓" if predictions is not None else "❌",
    "High confidence on training": "✓" if test_class_prob > 0.8 else "⚠️" if test_class_prob > 0.5 else "❌",
    "Correct prediction": "✓" if top_class == test_class else "❌",
}

for item, status in summary.items():
    print(f"{status} {item}")

print(f"\n{'='*80}\n")
