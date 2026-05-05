# Complete Implementation Guide: Safety Features & Grad-CAM Heatmaps

## Overview
This document provides step-by-step instructions to complete the deployment of safety features and Grad-CAM visualization for the skin disease AI system.

---

## Phase 1: Preparation (Already Complete ✓)

### What's Been Done
1. ✅ **model_tensorflow.py** - Complete rewrite with:
   - 8-class support (7 diseases + unknown)
   - Full Grad-CAM heatmap generation
   - Confidence threshold logic (0.60)
   - Unknown class rejection
   - Comprehensive debug logging
   - Error handling with proper response structure

2. ✅ **Frontend (ResultsPage.jsx)** - Updated to:
   - Conditionally display heatmap based on `is_valid_skin` flag
   - Show actual Grad-CAM image when valid
   - Display helpful messages for "No skin" or "Uncertain" cases
   - Support base64-encoded heatmap images

3. ✅ **New Training Script** - `train_with_unknown.py`
   - Supports 8 classes (including 'unknown')
   - Proper data augmentation
   - Base model freezing + fine-tuning strategy
   - Saves class indices with 8 classes

4. ✅ **Validation Script** - `validate_with_safety.py`
   - Tests real skin disease images
   - Tests non-skin image rejection
   - Validates confidence thresholds
   - Verifies heatmap generation
   - Checks debug information

5. ✅ **Dataset Generation** - `generate_unknown_dataset.py`
   - Creates 1000+ synthetic training images
   - Creates 280+ synthetic validation images
   - Generates: objects, textures, backgrounds, scenes, patterns, noise

---

## Phase 2: Dataset Preparation

### Step 1: Create Synthetic "Unknown" Dataset

**Run the dataset generation script:**
```bash
cd c:\hackthon angadi frontend\ml-service
python generate_unknown_dataset.py
```

**What it creates:**
- Directory: `../backend/data/train/unknown/` with 1000 synthetic images
- Directory: `../backend/data/val/unknown/` with 280 synthetic images
- Images include: objects, textures, backgrounds, indoor scenes, patterns, noise

**Verification:**
```bash
# Check training images
dir ..\backend\data\train\unknown | find /c ".jpg"

# Check validation images
dir ..\backend\data\val\unknown | find /c ".jpg"
```

**Expected output:** ~1000 training + ~280 validation images

---

## Phase 3: Model Training

### Step 2: Train with 8 Classes

**Run the enhanced training script:**
```bash
cd c:\hackthon angadi frontend\ml-service
python train_with_unknown.py
```

**What happens:**
1. Loads HAM10000 dataset (7 disease classes) + synthetic unknown class
2. Builds ResNet50 transfer learning model
3. Trains for up to 50 epochs with early stopping
4. Fine-tunes last 50 layers for additional 20 epochs
5. Saves:
   - `model_tensorflow_with_unknown.h5` (new model file)
   - `../backend/model/class_indices.json` (updated with 8 classes)
   - `training_history.json` (training metrics)

**Key configuration:**
- Image size: 224×224 (critical for consistency)
- Batch size: 32
- Learning rate: 0.001 (then 0.0001 for fine-tuning)
- Confidence threshold: 0.60 (in model_tensorflow.py)
- Epochs: 50 + 20 fine-tune

**Monitoring training:**
- Watch for validation accuracy convergence
- Check that loss decreases over epochs
- Monitor GPU memory usage

**Time estimate:** 20-40 minutes (depending on hardware)

---

## Phase 4: Validation & Testing

### Step 3: Run Comprehensive Tests

**Execute validation test suite:**
```bash
cd c:\hackthon angadi frontend\ml-service
python validate_with_safety.py
```

**What it tests:**
1. **TEST 1** - Real skin disease images should classify correctly
   - Loads first image from each disease class
   - Checks prediction confidence ≥ 0.60
   - Verifies heatmap generation for valid predictions

2. **TEST 2** - Non-skin rejection (gray background, noise, patterns)
   - Creates synthetic non-skin images
   - Verifies `is_valid_skin = False`
   - Checks that heatmap is `None`

3. **TEST 3** - Confidence threshold validation
   - Verifies confidence logic (≥ 0.60 for disease, < 0.60 for uncertain)
   - Checks that most real skin images exceed threshold

4. **TEST 4** - Grad-CAM heatmap generation
   - Tests heatmap creation for valid predictions
   - Verifies heatmap structure (width, height, base64 image)
   - Confirms heatmap is None for invalid predictions

5. **TEST 5** - Debug information completeness
   - Verifies all required debug fields are present
   - Checks: status, confidence_threshold, is_unknown_class, all_probabilities

**Expected results:**
```
TEST 1: ✓ PASS - disease images classified correctly
TEST 2: ✓ PASS - non-skin images rejected
TEST 3: ✓ PASS - confidence threshold working
TEST 4: ✓ PASS - heatmaps generated correctly
TEST 5: ✓ PASS - debug info complete
```

---

## Phase 5: Deployment

### Step 4: Deploy New Model

**Replace the old model with the new one:**
```bash
cd c:\hackthon angadi frontend\ml-service

# Backup old model
ren model_tensorflow.h5 model_tensorflow_backup.h5

# Deploy new model
ren model_tensorflow_with_unknown.h5 model_tensorflow.h5

# Verify class indices were updated
dir ..\backend\model\class_indices.json
```

**Verify class_indices.json has 8 classes:**
```bash
cat ..\backend\model\class_indices.json
```

Expected output:
```json
{
  "akiec": 0,
  "bcc": 1,
  "bkl": 2,
  "df": 3,
  "mel": 4,
  "nv": 5,
  "vasc": 6,
  "unknown": 7
}
```

---

## Phase 6: System Integration

### Step 5: Start/Restart Services

**Ensure all services are running:**

1. **Python ML Service** (inference server):
```bash
cd c:\hackthon angadi frontend\ml-service
python app.py
```
- Should run on http://127.0.0.1:8000
- Check endpoint: GET http://127.0.0.1:8000/health

2. **Node.js Backend API**:
```bash
cd c:\hackthon angadi frontend\backend
npm install  # If not done yet
node server.js
```
- Should run on http://127.0.0.1:5000
- Handles file uploads and calls ML service

3. **React Frontend**:
```bash
cd c:\hackthon angadi frontend\triage-app
npm run dev
```
- Should run on http://127.0.0.1:5173 (Vite dev server)
- Displays UI and handles image upload

**Services startup order:**
1. ML Service (port 8000) - must be ready first
2. Backend API (port 5000) - needs ML service
3. Frontend (port 5173) - can start anytime

---

## Phase 7: End-to-End Testing

### Step 6: Test Complete System

**Test with Real Skin Images:**
1. Open frontend: http://127.0.0.1:5173
2. Go to "Upload Page"
3. Upload a real skin disease image (melanoma, nevus, etc.)
4. Check results:
   - Prediction shows disease name ✓
   - Confidence > 60% ✓
   - "Show Heatmap" button appears ✓
   - Clicking heatmap shows red zones on lesion area ✓

**Test with Non-Skin Images:**
1. Upload a random object, indoor scene, or background
2. Check results:
   - Prediction shows "No skin detected" ✓
   - Heatmap section shows warning message ✓
   - No "Show Heatmap" button ✓

**Test with Low-Quality Images:**
1. Upload blurry or low-contrast skin image
2. Check results:
   - Prediction shows "Uncertain / Not a clear skin condition" ✓
   - Confidence < 60% ✓
   - Heatmap section shows warning message ✓

---

## System Architecture

### Request/Response Flow

```
Browser
  ↓
Frontend (React @ 5173)
  ├─ Takes image input
  ├─ Sends FormData to backend
  └─ Displays results with heatmap
  
  ↓
Backend API (Express @ 5000)
  ├─ Receives multipart/form-data
  ├─ Saves file temporarily
  ├─ Calls ML Service
  └─ Returns JSON response
  
  ↓
ML Service (TensorFlow @ 8000)
  ├─ Loads image (224×224)
  ├─ Preprocesses: img_array * (1/255)
  ├─ Runs inference: model.predict()
  ├─ Applies safety checks:
  │  ├─ is_unknown? → return "No skin"
  │  ├─ confidence < 0.60? → return "Uncertain"
  │  └─ else → valid disease prediction
  ├─ Generates Grad-CAM heatmap (only for valid)
  ├─ Encodes as base64 JPEG
  └─ Returns JSON:
     {
       "prediction": "Melanoma",
       "confidence": 0.92,
       "is_valid_skin": true,
       "is_confident": true,
       "heatmap": {
         "image": "base64_encoded_jpeg",
         "width": 224,
         "height": 224
       },
       "top_k": [...],
       "debug_info": {...},
       "warning": "..."
     }
  ↓
Backend → Frontend → Browser Display
```

---

## Key Configuration Constants

**In model_tensorflow.py:**
```python
CONFIDENCE_THRESHOLD = 0.60  # Minimum confidence for disease diagnosis
CLASS_LABELS = {
    'akiec': 'Actinic Keratosis/Intraepithelial Carcinoma',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'vasc': 'Vascular Lesions',
    'unknown': 'Non-Skin / Unknown / Background'
}
IMG_SIZE = (224, 224)  # Critical: must match training
RESCALE_FACTOR = 1/255  # Normalize pixel values
GRAD_CAM_LAYER = "conv5_block3_out"  # Last conv layer for ResNet50
COLORMAP = cv2.COLORMAP_JET  # Red for important, blue for less important
```

---

## Troubleshooting

### Issue: Model not found
**Solution:**
```bash
# Check if model file exists
ls -la c:\hackthon angadi frontend\ml-service\model_tensorflow.h5

# If missing, rename the training output
ren c:\hackthon angadi frontend\ml-service\model_tensorflow_with_unknown.h5 model_tensorflow.h5
```

### Issue: All predictions still "Uncertain"
**Possible causes:**
1. Model has less than 8 classes (old model)
   - Solution: Deploy new model_tensorflow_with_unknown.h5
2. Confidence threshold too high
   - Check: CONFIDENCE_THRESHOLD = 0.60 in model_tensorflow.py
3. Model weights not trained
   - Solution: Re-run train_with_unknown.py

### Issue: Heatmap not showing
**Possible causes:**
1. Backend not returning heatmap field
   - Check: is_valid_skin == True in response
2. Frontend expecting wrong field
   - Verify: storedResult.heatmap.image exists
3. Base64 encoding error
   - Check ML service logs for "heatmap" errors

### Issue: Non-skin images not rejected
**Possible causes:**
1. 'unknown' class not trained properly
   - Solution: Retrain with generate_unknown_dataset.py output
2. Synthetic images too similar to skin
   - Solution: Use real non-skin dataset (COCO, ImageNet, etc.)
3. Confidence threshold too low
   - Increase: CONFIDENCE_THRESHOLD from 0.60 to 0.70

### Issue: Heatmap highlights wrong area
**Possible causes:**
1. Wrong last conv layer name
   - For ResNet50: should be "conv5_block3_out"
   - Check: model.summary() to verify layer names
2. Gradient computation error
   - Add print statements in generate_gradcam_heatmap()
3. Image preprocessing mismatch
   - Verify: Same rescale (1/255) as training

---

## Performance Metrics to Monitor

After deployment, monitor:
1. **Inference time**: Should be < 2 seconds per image
2. **Heatmap generation**: Should be < 1 second
3. **Memory usage**: Model should be ~90 MB
4. **Accuracy**: Real skin diseases should classify correctly
5. **False positives**: Non-skin images should be rejected
6. **Confidence distribution**: Valid predictions > 60%, uncertain < 60%

---

## Next Steps

After successful deployment:
1. **Collect feedback** from users on predictions
2. **Monitor model performance** in production
3. **Retrain periodically** with new validated data
4. **Improve 'unknown' class** with real non-skin images
5. **Add user feedback loop** to improve accuracy
6. **Consider ensemble methods** for higher confidence

---

## References

**Key Files:**
- Training: `ml-service/train_with_unknown.py`
- Inference: `ml-service/model_tensorflow.py`
- Validation: `ml-service/validate_with_safety.py`
- Dataset Gen: `ml-service/generate_unknown_dataset.py`
- Frontend: `triage-app/src/pages/ResultsPage.jsx`

**Key Concepts:**
- **Grad-CAM**: Gradient-weighted Class Activation Mapping for explainability
- **Transfer Learning**: ResNet50 pre-trained on ImageNet
- **Safety Checks**: Confidence threshold + unknown class rejection
- **Heatmap**: Red (important) to blue (less important) visualization

**Technologies:**
- Backend: TensorFlow 2.x, Keras
- API: Express.js (Node.js)
- Frontend: React 18, Vite
- Visualization: Base64-encoded JPEG heatmaps
