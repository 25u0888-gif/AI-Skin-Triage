# Training/Inference Alignment Guide

## Overview

This guide ensures that your model training and inference use **EXACTLY** the same preprocessing and data format. Misalignment is the most common cause of poor model performance.

## Critical Alignment Points

### 1. Image Size (MUST MATCH)
```
Training: IMG_SIZE = (224, 224)
Inference: target_size=(224, 224)
```

### 2. Image Preprocessing (MUST MATCH)

#### Training Preprocessing
```python
# train_tensorflow.py
train_datagen = ImageDataGenerator(rescale=1./255)
train_data = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)
```

**What happens internally:**
1. Load image: `cv2.imread()` or PIL `load_img()` → (224, 224, 3) with values [0, 255]
2. Convert to array: `img_to_array()` → (224, 224, 3) with values [0, 255]
3. Rescale: `* (1./255)` → (224, 224, 3) with values [0, 1]
4. Add batch: `flow_from_directory` handles this → (batch, 224, 224, 3)

#### Inference Preprocessing (MUST MATCH EXACTLY)
```python
# model_tensorflow.py - preprocess_image()
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Step 1: Load with target size
img = load_img(image_path, target_size=(224, 224))

# Step 2: Convert to array
img_array = img_to_array(img)

# Step 3: Rescale by 1/255 (SAME AS TRAINING)
img_array = img_array * (1./255)

# Step 4: Add batch dimension
img_array = np.expand_dims(img_array, axis=0)

# Now shape is (1, 224, 224, 3) with values [0, 1]
```

### 3. Class Indices Mapping (MUST MATCH)

#### During Training
```python
# train_tensorflow.py - STEP 3: Load Data
train_data = train_datagen.flow_from_directory(TRAIN_DIR, ...)

# Print class indices
print(train_data.class_indices)
# Output: {'akiec': 0, 'bcc': 1, 'bkl': 2, 'df': 3, 'mel': 4, 'nv': 5, 'vasc': 6}

# SAVE them
class_indices_path = "../backend/model/class_indices.json"
with open(class_indices_path, 'w') as f:
    json.dump(train_data.class_indices, f, indent=2)
```

#### During Inference
```python
# model_tensorflow.py - load_class_indices()
# Load SAME class indices
with open(class_indices_path, 'r') as f:
    class_to_idx = json.load(f)

# Reverse to get index-to-class mapping
idx_to_class = {int(v): k for k, v in class_to_idx.items()}
# Output: {0: 'akiec', 1: 'bcc', 2: 'bkl', 3: 'df', 4: 'mel', 5: 'nv', 6: 'vasc'}

# Use this to interpret predictions
top_idx = np.argmax(predictions)
top_class = idx_to_class[top_idx]
```

### 4. Model Architecture (MUST MATCH)

#### Training Model
```python
# train_tensorflow.py - STEP 4: Build Model
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224,224,3))
base_model.trainable = False

inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.3)(x)
outputs = Dense(7, activation='softmax')(x)

model = Model(inputs, outputs)
```

#### Inference Model (AUTO - just load the saved model)
```python
# model_tensorflow.py - load_tensorflow_model()
model = tf.keras.models.load_model(MODEL_PATH)
# ✓ Model architecture is loaded automatically - no need to rebuild!
```

## Verification Checklist

### Before Training
- [ ] Dataset structure: `data/train/class1/`, `data/train/class2/`, etc.
- [ ] Metadata file: `../backend/data/HAM10000_metadata.csv`
- [ ] Image directories exist: `HAM10000_images_part_1/`, `HAM10000_images_part_2/`

### During Training
- [ ] Class indices printed: `✓ {0: 'akiec', 1: 'bcc', ...}`
- [ ] Training samples counted: `✓ Training data loaded from train/`
- [ ] Model architecture logged: `✓ Model loaded successfully`
- [ ] Epochs completed: `✓ Training complete!`

### After Training
- [ ] Model file saved: `model_tensorflow.h5` (should be ~92 MB)
- [ ] Class indices saved: `../backend/model/class_indices.json`
- [ ] Training history saved: `training_history.json`

### Before Inference
- [ ] Model file exists: `model_tensorflow.h5`
- [ ] Class indices exist: `../backend/model/class_indices.json`
- [ ] Image size = 224x224
- [ ] Preprocessing rescale factor = 1/255

## Testing Alignment

### Test 1: Validate Training Setup
```bash
cd ml-service
python validate_training.py
```

This checks:
- ✓ Dataset structure
- ✓ Class indices saved
- ✓ Model file exists
- ✓ Image preprocessing matches
- ✓ Dataset balance

### Test 2: Inference on Training Images
```bash
python test_inference.py
```

This verifies:
- ✓ Image preprocessing works
- ✓ Model loads correctly
- ✓ Predictions are generated
- ✓ Confidence is high (>80%) on training images
- ✓ Correct class is predicted

### Test 3: Quick Prediction Test
```bash
python model_switcher.py test /path/to/image.jpg
```

## Debugging Misalignment

### Issue: "Model predictions always same confidence"
**Cause:** All preprocessing steps not matching
**Fix:**
1. Check image rescale: Should be exactly `image / 255`
2. Check image size: Should be exactly (224, 224)
3. Verify class indices match between training and inference

### Issue: "Model confidence < 50% on training images"
**Cause:** Preprocessing mismatch or model not trained
**Fix:**
1. Run `python test_inference.py` to see what's wrong
2. Check if IMG_SIZE, rescale, and order match
3. Run training longer: Increase EPOCHS to 20-50

### Issue: "Different predictions each time for same image"
**Cause:** Probably not a mismatch (if using same preprocessing)
**Note:** Normal if model uses dropout (remove `training=False` if you want deterministic)

### Issue: "Class indices don't match between training and inference"
**Cause:** Class indices file not saved or updated
**Fix:**
1. Check: `cat ../backend/model/class_indices.json`
2. Re-run training to regenerate: `python train_tensorflow.py`

## Exact Code References

### Training (train_tensorflow.py)
```python
# Line ~70: Image preprocessing
IMG_SIZE = (224, 224)
train_datagen = ImageDataGenerator(rescale=1./255, ...)

# Line ~130: Print class indices
print(train_data.class_indices)

# Line ~200: Save class indices
with open(CLASS_INDICES_PATH, 'w') as f:
    json.dump(class_indices, f, indent=2)

# Line ~250: Save model
model.save(MODEL_PATH, save_format='h5')
```

### Inference (model_tensorflow.py)
```python
# Line ~80: Load class indices
idx_to_class = load_class_indices()

# Line ~130: Preprocess image
img = load_img(image_path, target_size=(224, 224))
img_array = img_to_array(img)
img_array = img_array * (1./255)  # Must match training
img_array = np.expand_dims(img_array, axis=0)

# Line ~150: Get predictions
predictions = model.predict(img_array, verbose=0)
probs = predictions[0]

# Line ~165: Map to class name
top_idx = np.argmax(probs)
top_class = idx_to_class[top_idx]
```

## Expected Performance

### If Everything Aligned Correctly
- ✓ Confidence on training images: > 80%
- ✓ Correct class predicted: Yes (for most training images)
- ✓ Different images give different predictions: Yes
- ✓ Consistent predictions for same image: Yes

### If Misaligned
- ❌ Confidence always ~14% (random guess with 7 classes)
- ❌ Same prediction for all images
- ❌ Incorrect predictions on training images
- ❌ Model fails with shape errors

## Commands Quick Reference

```bash
# Prepare dataset
python prepare_dataset.py

# Train model
python train_tensorflow.py

# Validate alignment
python validate_training.py

# Test inference on training data
python test_inference.py

# Quick test on any image
python model_switcher.py test /path/to/image.jpg

# Switch backends
python model_switcher.py set-tensorflow
python model_switcher.py set-pytorch

# Check status
python model_switcher.py status
```

## Summary

**The Key Principle: Training and Inference Must Be Identical**

| Component | Training | Inference | Alignment |
|-----------|----------|-----------|-----------|
| Image Size | (224, 224) | (224, 224) | ✓ Must match |
| Rescale | 1/255 | 1/255 | ✓ Must match |
| Class Indices | Saved to JSON | Load from JSON | ✓ Must match |
| Model | ResNet50+Dense | Load same file | ✓ Auto matched |
| Batch Shape | (B, 224, 224, 3) | (1, 224, 224, 3) | ✓ Must match |
| Value Range | [0, 1] | [0, 1] | ✓ Must match |

**When in doubt, use `test_inference.py` to debug!**
