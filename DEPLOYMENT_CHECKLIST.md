# 📋 DEPLOYMENT CHECKLIST

Use this checklist to track your progress through the deployment process.

---

## Phase 1: Preparation ✅ (Already Complete)
- [x] Core model_tensorflow.py rewritten with Grad-CAM
- [x] Frontend (ResultsPage.jsx) updated for conditional heatmap
- [x] Training script created (train_with_unknown.py)
- [x] Validation script created (validate_with_safety.py)
- [x] Dataset generator created (generate_unknown_dataset.py)
- [x] Documentation created (IMPLEMENTATION_GUIDE.md)

---

## Phase 2: Dataset Generation
**Time: ~5 minutes**

### Command
```bash
cd c:\hackthon angadi frontend\ml-service
python generate_unknown_dataset.py
```

**Progress:**
- [ ] Script starts without errors
- [ ] Generates training/unknown directory
- [ ] Generates validation/unknown directory
- [ ] Creates ~1000 training images
- [ ] Creates ~280 validation images

**Verification:**
```bash
# Check image counts
dir c:\hackthon angadi frontend\backend\data\train\unknown | find /c ".jpg"
dir c:\hackthon angadi frontend\backend\data\val\unknown | find /c ".jpg"
```

**Expected Output:** ~1000 training + ~280 validation images

---

## Phase 3: Model Training
**Time: ~20-40 minutes (depending on GPU)**

### Command
```bash
cd c:\hackthon angadi frontend\ml-service
python train_with_unknown.py
```

**Progress:**
- [ ] Script loads training data successfully
- [ ] Script loads validation data successfully
- [ ] ResNet50 base model loads from ImageNet
- [ ] Model compiles without errors
- [ ] Training starts (watch epoch progress)
- [ ] Validation accuracy improves over epochs
- [ ] Training completes successfully

**What to Monitor:**
- Watch training loss decreases ✓
- Watch validation accuracy increases ✓
- Epochs should not be stuck ✓
- Memory usage reasonable ✓

**Output Files:**
- [ ] `model_tensorflow_with_unknown.h5` created (~90 MB)
- [ ] `../backend/model/class_indices.json` updated (8 classes)
- [ ] `training_history.json` created

**Verification:**
```bash
# Check model file created
dir c:\hackthon angadi frontend\ml-service\*.h5

# Check class indices (should have 8 classes)
type c:\hackthon angadi frontend\backend\model\class_indices.json
```

---

## Phase 4: Validation Testing
**Time: ~5-10 minutes**

### Command
```bash
cd c:\hackthon angadi frontend\ml-service
python validate_with_safety.py
```

**Tests to Verify:**
- [ ] TEST 1: Real skin disease images - ✓ PASS
- [ ] TEST 2: Non-skin image rejection - ✓ PASS
- [ ] TEST 3: Confidence threshold logic - ✓ PASS
- [ ] TEST 4: Grad-CAM heatmap generation - ✓ PASS
- [ ] TEST 5: Debug information - ✓ PASS

**Expected Results:**
- All 5 tests should PASS
- Real skin diseases classified correctly
- Non-skin images returned "No skin"
- Heatmaps generated for valid predictions
- Debug information complete

**If Tests Fail:**
- [ ] Check error messages
- [ ] Verify model file loaded correctly
- [ ] Check class indices have 8 classes
- [ ] Review test output for specific failures

---

## Phase 5: Model Deployment
**Time: ~2 minutes**

### Step 1: Backup Old Model
```bash
cd c:\hackthon angadi frontend\ml-service
ren model_tensorflow.h5 model_tensorflow_backup.h5
```
- [ ] Old model backed up

### Step 2: Deploy New Model
```bash
ren model_tensorflow_with_unknown.h5 model_tensorflow.h5
```
- [ ] New model deployed

### Step 3: Verify Files
```bash
# Should show model_tensorflow.h5 (NOT model_tensorflow_with_unknown.h5)
dir c:\hackthon angadi frontend\ml-service\*.h5

# Verify class indices has 8 classes
type c:\hackthon angadi frontend\backend\model\class_indices.json
```

**Checklist:**
- [ ] Old model backed up as `model_tensorflow_backup.h5`
- [ ] New model deployed as `model_tensorflow.h5`
- [ ] File size ~90 MB (ResNet50)
- [ ] Class indices show 8 classes including 'unknown'

---

## Phase 6: Service Startup
**Time: ~2 minutes**

### Terminal 1: ML Service
```bash
cd c:\hackthon angadi frontend\ml-service
python app.py
```

**Progress:**
- [ ] Dependencies import successfully
- [ ] Model loads into memory
- [ ] Server starts on port 8000
- [ ] Logs show: "Running on http://127.0.0.1:8000"

**Health Check:**
```bash
# In another terminal
curl http://127.0.0.1:8000/health
```

### Terminal 2: Backend API
```bash
cd c:\hackthon angadi frontend\backend
node server.js
```

**Progress:**
- [ ] Dependencies resolve
- [ ] Server starts on port 5000
- [ ] Logs show: "Server running on port 5000"

### Terminal 3: Frontend
```bash
cd c:\hackthon angadi frontend\triage-app
npm run dev
```

**Progress:**
- [ ] Vite dev server starts
- [ ] Logs show: "Local: http://localhost:5173"
- [ ] No errors in console

**Service Verification:**
- [ ] ML Service: `curl http://127.0.0.1:8000/health` → Returns OK
- [ ] Backend: `curl http://127.0.0.1:5000/` → Returns 200
- [ ] Frontend: Opens in browser without errors

---

## Phase 7: End-to-End Testing
**Time: ~10 minutes**

### Test 1: Real Skin Disease Image
1. [ ] Open http://127.0.0.1:5173
2. [ ] Click "Upload Image"
3. [ ] Select melanoma or nevus image
4. [ ] Click "Analyze"
5. [ ] Wait for results

**Expected Results:**
- [ ] Shows disease name (not "Uncertain")
- [ ] Confidence > 60%
- [ ] "Show Heatmap" button visible
- [ ] Clicking heatmap shows red zones on lesion
- [ ] Heatmap makes visual sense (highlights skin lesion area)

### Test 2: Non-Skin Image
1. [ ] Go back to upload page
2. [ ] Select non-skin image (object, background, etc.)
3. [ ] Click "Analyze"
4. [ ] Wait for results

**Expected Results:**
- [ ] Shows "No skin detected"
- [ ] NO "Show Heatmap" button
- [ ] Heatmap section shows warning message
- [ ] Confidence may be high for "unknown" class
- [ ] System correctly rejects non-skin image

### Test 3: Low-Quality Image
1. [ ] Upload blurry or unclear skin image
2. [ ] Click "Analyze"

**Expected Results:**
- [ ] Shows "Uncertain / Not a clear skin condition"
- [ ] Confidence < 60%
- [ ] NO "Show Heatmap" button
- [ ] Heatmap section shows warning message

### Test 4: Heatmap Visualization
1. [ ] Analyze a valid skin disease image
2. [ ] Click "Show Heatmap" button
3. [ ] Observe heatmap display

**Expected Results:**
- [ ] Heatmap loads without errors
- [ ] Red zones highlight lesion area
- [ ] Image is readable (not completely red)
- [ ] Colors transition from red → yellow → blue
- [ ] Toggle between original and heatmap works

---

## Phase 8: Browser Console Verification
**Time: ~2 minutes**

### Check Frontend Logs
1. [ ] Open Developer Tools (F12)
2. [ ] Go to Console tab
3. [ ] Analyze results with heatmap

**Expected in Console:**
- [ ] No errors (red messages)
- [ ] No 404 errors for heatmap image
- [ ] localStorage contains result data
- [ ] heatmap.image contains base64 data

### Check Network Logs
1. [ ] Open Network tab
2. [ ] Analyze a skin disease image
3. [ ] Watch network requests

**Expected Requests:**
- [ ] POST to `/analyze` endpoint
- [ ] Response contains `heatmap` field
- [ ] Response status: 200 OK
- [ ] Heatmap size reasonable (~50-100 KB)

---

## Phase 9: Final Verification
**Time: ~5 minutes**

### Model Functionality
- [ ] 8 classes loaded correctly
- [ ] ResNet50 weights loaded
- [ ] Class indices match model output
- [ ] Preprocessing correct (224×224, rescale 1/255)

### Safety Features
- [ ] Non-skin images rejected (unknown class)
- [ ] Confidence threshold enforced (0.60)
- [ ] Low-confidence predictions flagged as "Uncertain"
- [ ] Valid predictions show both disease and confidence

### Explainability Features
- [ ] Grad-CAM heatmaps generated
- [ ] Heatmap shows in red/yellow/blue colormap
- [ ] Heatmap highlights relevant areas
- [ ] Heatmap only shown for valid predictions
- [ ] Heatmap hidden for "No skin" or "Uncertain"

### Frontend Display
- [ ] Results page shows correctly
- [ ] Heatmap toggle button appears/disappears appropriately
- [ ] Warning messages clear and helpful
- [ ] All text readable and well-formatted
- [ ] Responsive on different screen sizes

### Logging & Debug
- [ ] ML service logs show 8-step prediction pipeline
- [ ] Debug info includes all probabilities
- [ ] Confidence threshold logged
- [ ] Unknown class detection logged
- [ ] No errors in any service logs

---

## Success Criteria

✅ **All of the following must be true:**
1. [ ] Generate script created 1280+ synthetic images
2. [ ] Training completed successfully with 8 classes
3. [ ] Validation tests all passed
4. [ ] Model deployed as model_tensorflow.h5
5. [ ] All 3 services running without errors
6. [ ] Real skin disease → correct prediction + heatmap
7. [ ] Non-skin image → "No skin detected" + no heatmap
8. [ ] Low-quality image → "Uncertain" + no heatmap
9. [ ] Heatmap visualization works correctly
10. [ ] No console errors or warnings

---

## Troubleshooting Quick Links

**Model Loading Issues:**
- Check: model_tensorflow.h5 exists and is ~90 MB
- Check: class_indices.json has 8 classes
- Check: No old .pyc files cached

**Training Issues:**
- Check: Data directories exist with subdirectories
- Check: Unknown directory has generated images
- Check: GPU memory available (or use CPU with patience)

**Prediction Issues:**
- Check: Model loaded correctly in ML service
- Check: Image preprocessing uses (224, 224) and rescale 1/255
- Check: Confidence threshold is 0.60

**Heatmap Issues:**
- Check: is_valid_skin=True in response
- Check: confidence > 0.60
- Check: prediction is not "unknown"
- Check: Base64 encoding successful

**Frontend Issues:**
- Check: No JavaScript errors in console
- Check: ResultsPage.jsx has conditional heatmap code
- Check: localStorage contains result data

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Preparation | - | ✅ Complete |
| Phase 2: Dataset Gen | 5 min | ⏳ Ready |
| Phase 3: Training | 20-40 min | ⏳ Ready |
| Phase 4: Validation | 5-10 min | ⏳ Ready |
| Phase 5: Deployment | 2 min | ⏳ Ready |
| Phase 6: Startup | 2 min | ⏳ Ready |
| Phase 7: End-to-End | 10 min | ⏳ Ready |
| Phase 8: Console Check | 2 min | ⏳ Ready |
| Phase 9: Verification | 5 min | ⏳ Ready |
| **TOTAL** | **~1 hour** | - |

---

## Notes

- Dataset generation is fastest (~5 min)
- Model training takes longest (20-40 min, depends on GPU)
- All other phases are quick (< 10 min each)
- GPU recommended but not required
- Validation tests give confidence that everything works

---

**When complete, you'll have a production-ready system with:**
- ✅ Non-skin image rejection
- ✅ Confidence-based safety checks
- ✅ Grad-CAM explainability
- ✅ Conditional heatmap display
- ✅ Full error handling
- ✅ Comprehensive debugging

**Start with Phase 2 and follow the checklist step by step!**
