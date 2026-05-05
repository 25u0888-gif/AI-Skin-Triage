# ✅ TRAINING/INFERENCE ALIGNMENT - VERIFICATION CHECKLIST

Print this page and check off items as you complete them.

---

## 📋 PRE-EXECUTION CHECKLIST

Before you start, verify these prerequisites:

```
PREREQUISITES
├─ [ ] Python 3.8+ installed
├─ [ ] TensorFlow installed (or will install: pip install tensorflow)
├─ [ ] HAM10000 dataset files exist:
│  ├─ [ ] ../backend/data/HAM10000_metadata.csv
│  ├─ [ ] ../backend/data/HAM10000_images_part_1/ directory
│  └─ [ ] ../backend/data/HAM10000_images_part_2/ directory
├─ [ ] All 7 implementation files exist in ml-service/:
│  ├─ [ ] prepare_dataset.py
│  ├─ [ ] train_tensorflow.py
│  ├─ [ ] model_tensorflow.py
│  ├─ [ ] validate_training.py
│  ├─ [ ] test_inference.py
│  ├─ [ ] model_switcher.py
│  └─ [ ] run_pipeline.py
├─ [ ] All 7 documentation files exist:
│  ├─ [ ] ACTION_PLAN.md
│  ├─ [ ] ALIGNMENT_GUIDE.md
│  ├─ [ ] INDEX.md
│  ├─ [ ] README_SOLUTION.md
│  ├─ [ ] IMPLEMENTATION_COMPLETE.md
│  ├─ [ ] README_TENSORFLOW.md
│  └─ [ ] SWITCHER_GUIDE.md
└─ [ ] You have 30-50 minutes available (mostly waiting)

ISSUES TO RESOLVE BEFORE STARTING:
├─ [ ] If HAM10000 missing: Download from Kaggle
├─ [ ] If files missing: Check git clone completed
├─ [ ] If TensorFlow missing: pip install tensorflow
└─ [ ] If time limited: Save run_pipeline.py for later
```

---

## 🚀 EXECUTION CHECKLIST

Follow these steps in order. Check off each as you complete.

### STEP 1: Read the Plan
```
⏱️ Time: 5 minutes

ACTIONS:
└─ [ ] Open and read: ACTION_PLAN.md

VERIFICATION:
└─ [ ] You understand what each step does
    └─ [ ] You know why each step matters
    └─ [ ] You know what to expect in output
```

### STEP 2: Prepare Dataset
```
⏱️ Time: 3-5 minutes

COMMAND:
cd ml-service
python prepare_dataset.py

EXPECTED OUTPUT:
├─ [ ] "✓ Dataset preparation starting"
├─ [ ] "✓ [number] images found"
├─ [ ] "✓ Creating train/val split"
├─ [ ] "✓ train/ directory created"
├─ [ ] "✓ val/ directory created"
└─ [ ] "✓ Statistics:" followed by class counts

VERIFICATION:
└─ [ ] Check directories created:
    ├─ [ ] ../backend/data/train/ exists
    └─ [ ] ../backend/data/val/ exists
└─ [ ] Check class subdirectories exist:
    ├─ [ ] train/akiec/ has images
    ├─ [ ] train/bcc/ has images
    ├─ [ ] ... (7 classes total)
    └─ [ ] val/[classes]/ have images

ISSUES?
├─ [ ] "Image not found error" → Check HAM10000 path
├─ [ ] "Permission denied" → Check directory permissions
├─ [ ] "Out of memory" → Close other programs
└─ [ ] See ACTION_PLAN.md troubleshooting section
```

### STEP 3: Train Model
```
⏱️ Time: 10-30 minutes (mostly waiting - grab coffee ☕)

COMMAND:
python train_tensorflow.py

EXPECTED OUTPUT (in order):
├─ [ ] "STEP 1: Setup ✓"
├─ [ ] "STEP 2: Load Data ✓"
├─ [ ] "Training data loaded from train/"
├─ [ ] "Class indices: {0: 'akiec', 1: 'bcc', ...}"
├─ [ ] "STEP 3: Build Model ✓"
├─ [ ] "Model loaded successfully"
├─ [ ] "STEP 4: Train ✓"
├─ [ ] "Epoch 1/50" and progress...
├─ [ ] Epochs continue (may stop early with early stopping)
├─ [ ] "Training complete!"
├─ [ ] "STEP 5: Save ✓"
├─ [ ] "Model saved to model_tensorflow.h5"
└─ [ ] "Class indices saved"

VERIFICATION:
Check files created:
├─ [ ] model_tensorflow.h5 exists
│       Command: ls -lh model_tensorflow.h5
│       ├─ [ ] File size: ~92 MB
│       └─ [ ] File size is NOT 0 bytes (not empty!)
│
├─ [ ] ../backend/model/class_indices.json exists
│       Command: ls -l ../backend/model/class_indices.json
│
└─ [ ] training_history.json exists (optional)
        Command: ls -l training_history.json

Check file contents:
├─ [ ] class_indices.json contains 7 classes:
        cat ../backend/model/class_indices.json
        ├─ [ ] "akiec": 0
        ├─ [ ] "bcc": 1
        ├─ [ ] "bkl": 2
        ├─ [ ] "df": 3
        ├─ [ ] "mel": 4
        ├─ [ ] "nv": 5
        └─ [ ] "vasc": 6

ISSUES?
├─ [ ] "Out of memory" → Reduce BATCH_SIZE to 16, EPOCHS to 30
├─ [ ] "GPU out of memory" → Model file will still be created (check STEP 5)
├─ [ ] "Training stopped early" → This is OK (early stopping triggered)
├─ [ ] "Model file is 0 bytes" → Error during training, check logs
└─ [ ] See ACTION_PLAN.md troubleshooting section
```

### STEP 4: Validate Training
```
⏱️ Time: 2 minutes

COMMAND:
python validate_training.py

EXPECTED OUTPUT:
├─ [ ] "VALIDATION STARTING"
├─ [ ] "Checking prerequisites:"
├─ [ ] "✓ Class indices file exists"
├─ [ ] "✓ Model file exists"
├─ [ ] "✓ Training data exists"
├─ [ ] "✓ Validation data exists"
├─ [ ] "Dataset Statistics:"
├─ [ ] "  ✓ Training samples: [number]"
├─ [ ] "  ✓ Validation samples: [number]"
├─ [ ] "  ✓ Class distribution: [balanced stats]"
└─ [ ] "VALIDATION COMPLETE ✓"

VERIFICATION:
├─ [ ] All checks show ✓ (not ❌)
├─ [ ] Class indices match expected: {0: 'akiec', ...}
├─ [ ] Training data > 8000 images
├─ [ ] Validation data > 2000 images
└─ [ ] Class distribution is balanced (±5% difference)

ISSUES?
├─ [ ] "❌ Class indices missing" → Re-run train_tensorflow.py
├─ [ ] "❌ Model file missing" → Check Step 3 output
├─ [ ] "❌ Training data missing" → Re-run prepare_dataset.py
└─ [ ] See ACTION_PLAN.md troubleshooting section
```

### STEP 5: Test Inference Alignment
```
⏱️ Time: 3-5 minutes

COMMAND:
python test_inference.py

EXPECTED OUTPUT (Critical Checks):
├─ [ ] "TRAINING/INFERENCE ALIGNMENT TEST"
├─ [ ] "Checking prerequisites..."
├─ [ ] "✓ All prerequisites met"
│
├─ [ ] "TEST 1: Image Preprocessing"
│       ├─ [ ] "✓ Image loaded"
│       ├─ [ ] "✓ Converted to array, shape: (224, 224, 3)"
│       ├─ [ ] "✓ Rescaled by 1/255"
│       └─ [ ] "✓ Added batch dimension, shape: (1, 224, 224, 3)"
│
├─ [ ] "TEST 2: Model Prediction"
│       ├─ [ ] "✓ Predictions generated"
│       └─ [ ] Full prediction breakdown shown
│
├─ [ ] "TEST 3: Confidence Analysis"
│       ├─ [ ] Shows predictions with percentages
│       ├─ [ ] "✓ MODEL IS CORRECT!" (top prediction = true class)
│       └─ [ ] "✓ HIGH CONFIDENCE (>80%)" ← CRITICAL!
│
├─ [ ] "TEST 4: Batch Processing"
│       ├─ [ ] "✓ Data flow created"
│       ├─ [ ] "✓ Batch retrieved"
│       ├─ [ ] "✓ Batch predictions"
│       └─ [ ] Shows 5 sample predictions
│
├─ [ ] "TEST 5: Recommendations"
│       ├─ If issues: Shows specific fixes
│       └─ If OK: "✓ Model is performing well!"
│
└─ [ ] "TEST SUMMARY" shows mostly ✓ (not ❌)
```

### CRITICAL VERIFICATION
```
For model to be production-ready, ALL must be TRUE:

┌─────────────────────────────────────────┐
│ MUST HAVE ✓ (Not ❌)                     │
├─────────────────────────────────────────┤
│ ✓ Preprocessing match                    │
│ ✓ Model makes predictions                │
│ ✓ HIGH CONFIDENCE (>80%)                 │
│ ✓ Correct class predicted                │
│ ✓ Batch processing works                 │
│ ✓ Model file size: 90+ MB                │
│ ✓ Class indices: 7 classes               │
│ ✓ Same prediction for same image         │
└─────────────────────────────────────────┘

If ANY are ❌:
├─ [ ] Check test_inference.py output carefully
├─ [ ] Read ALIGNMENT_GUIDE.md section on that issue
├─ [ ] See ACTION_PLAN.md troubleshooting
└─ [ ] Re-run training with more epochs if confidence too low
```

ISSUES?
├─ [ ] "Confidence < 50%" → Model needs more training (re-run train_tensorflow.py)
├─ [ ] "Wrong class predicted" → Check class indices match
├─ [ ] "Preprocessing doesn't match" → Check model_tensorflow.py preprocess_image()
├─ [ ] "Model not found" → Verify Step 3 output, check model file exists
└─ [ ] See ACTION_PLAN.md troubleshooting section
```

---

## 🎯 POST-EXECUTION CHECKLIST

### After All Tests Pass
```
CONFIRM SUCCESS:
├─ [ ] test_inference.py shows mostly ✓ (green checkmarks)
├─ [ ] Confidence is > 80% on training images
├─ [ ] Correct class was predicted
├─ [ ] Model file is 90+ MB (not empty)
├─ [ ] Class indices file has 7 classes
└─ [ ] All raw predictions are reasonable (not all same)

YOU CAN NOW:
├─ [ ] Deploy model to production
├─ [ ] Update backend to use TensorFlow
├─ [ ] Restart services
├─ [ ] Test with real images from frontend
└─ [ ] Monitor prediction confidence in logs
```

### Deployment
```
COMMAND:
python model_switcher.py set-tensorflow

VERIFICATION:
├─ [ ] Command completes without error
├─ [ ] model_config.json shows: {"backend": "tensorflow"}
└─ [ ] Backend can import and use model

FINAL TEST:
python model_switcher.py test /path/to/test/image.jpg

EXPECTED OUTPUT:
├─ [ ] Image loaded
├─ [ ] Prediction generated
├─ [ ] Confidence shown as percentage
└─ [ ] Result JSON displayed
```

---

## 📊 RESULTS SUMMARY

### Success Criteria Met
```
On a scale of 1-10:

Preprocessing Alignment:    ___/10
Model Performance:          ___/10
Confidence Levels:          ___/10
Prediction Consistency:     ___/10
Overall System Status:      ___/10

Target: All scores ≥ 8/10
Status: [ ] PASS [ ] NEEDS IMPROVEMENT [ ] FAILED
```

### Model Statistics
```
Fill in after training completes:

Model File Size: __________ MB (Should be ~92 MB)
Number of Classes: __________ (Should be 7)
Training Accuracy: __________%
Validation Accuracy: __________%
Epochs Trained: __________ (Out of 50 max)
Training Time: __________ minutes
Confidence on Training Images: __________%
```

---

## 🚨 EMERGENCY TROUBLESHOOTING

If something goes wrong, follow this:

```
STEP 1: Check Logs
└─ [ ] Run test_inference.py again
└─ [ ] Look at exact error message
└─ [ ] Note the error

STEP 2: Look Up Error
├─ [ ] Check ACTION_PLAN.md troubleshooting section
├─ [ ] Check ALIGNMENT_GUIDE.md debugging section
└─ [ ] Check test_inference.py output for specific fix

STEP 3: Common Fixes
├─ [ ] Low confidence? → Re-train with more epochs
├─ [ ] Wrong class? → Check class_indices.json format
├─ [ ] Preprocessing error? → Compare with ALIGNMENT_GUIDE.md
├─ [ ] Model not found? → Re-run train_tensorflow.py
└─ [ ] Still stuck? → Check all prerequisites again (STEP 1)

STEP 4: Last Resort
├─ [ ] Delete: model_tensorflow.h5
├─ [ ] Delete: class_indices.json
├─ [ ] Delete: training_history.json
├─ [ ] Re-run: python train_tensorflow.py
└─ [ ] Start from STEP 3 of this checklist
```

---

## 📝 NOTES SECTION

Use this space to write down:
- What you were doing when error occurred
- Exact error messages
- Times of execution
- Any unexpected behaviors

```
Date: ________________

What I was doing:
__________________________________________________________________

Error message (if any):
__________________________________________________________________

Output:
__________________________________________________________________

Resolution:
__________________________________________________________________

Notes for next time:
__________________________________________________________________
```

---

## 🎉 FINAL CHECKLIST

```
BEFORE YOU DECLARE SUCCESS:

├─ [ ] Read through ACTION_PLAN.md at least once
├─ [ ] Ran all 4 main commands in order:
│       1. [ ] prepare_dataset.py
│       2. [ ] train_tensorflow.py
│       3. [ ] validate_training.py
│       4. [ ] test_inference.py
│
├─ [ ] test_inference.py shows:
│       ├─ [ ] ✓ Preprocessing match
│       ├─ [ ] ✓ Model predictions generated
│       ├─ [ ] ✓ HIGH CONFIDENCE (>80%)
│       ├─ [ ] ✓ Correct class predicted
│       └─ [ ] ✓ Batch processing works
│
├─ [ ] Model files exist and correct size:
│       ├─ [ ] model_tensorflow.h5 ≈ 92 MB
│       ├─ [ ] class_indices.json exists
│       └─ [ ] training_history.json exists
│
└─ [ ] Ready to deploy!
       └─ [ ] Run: python model_switcher.py set-tensorflow
       └─ [ ] Restart backend service
       └─ [ ] Test with frontend

🎉 YOU'RE DONE! 🎉

The training/inference alignment is complete!
Your model is now production-ready!
```

---

## 📞 HELP RESOURCES (In This Order)

1. **test_inference.py output** - Shows exact errors with solutions
2. **ACTION_PLAN.md** - Troubleshooting section (5 min)
3. **ALIGNMENT_GUIDE.md** - Detailed debugging guide (10 min)
4. **README_SOLUTION.md** - Visual overview (5 min)

---

## ✨ Remember

- ✅ Follow steps in order
- ✅ Don't skip validation
- ✅ Don't ignore error messages
- ✅ Check file sizes (non-zero!)
- ✅ Verify confidence > 80%
- ✅ Test thoroughly before deployment

Good luck! 🚀

---

**PRINT THIS PAGE AND CHECK OFF ITEMS AS YOU GO!**

```
═══════════════════════════════════════════════════════
        Good luck with your training! 🎯
    Follow the checklist step-by-step and you'll succeed!
═══════════════════════════════════════════════════════
```
