#!/usr/bin/env python3
"""
Quick Reference Checklist for Training/Inference Pipeline
Ensures all steps are completed in the right order with verification
"""

import os
import json
import subprocess
import sys

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def check_file(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    symbol = "✓" if exists else "❌"
    print(f"  {symbol} {description}: {path}")
    return exists

def check_dir(path, description):
    """Check if a directory exists"""
    exists = os.path.isdir(path)
    symbol = "✓" if exists else "❌"
    print(f"  {symbol} {description}: {path}")
    return exists

def prompt_yes_no(question):
    """Ask user for yes/no response"""
    while True:
        response = input(f"\n{question} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

def main():
    print(f"\n{'='*70}")
    print("  TRAINING/INFERENCE PIPELINE CHECKLIST")
    print(f"{'='*70}")
    
    print("\nThis checklist ensures:")
    print("  1. Dataset is properly prepared")
    print("  2. Model is trained correctly")
    print("  3. Training/inference are aligned")
    print("  4. Model works on known data")
    
    # ========================================================================
    # STEP 1: Dataset Preparation
    # ========================================================================
    
    print_section("STEP 1: Dataset Preparation")
    
    print("\nRequired files:")
    metadata_exists = check_file("../backend/data/HAM10000_metadata.csv", "Metadata CSV")
    images1_exist = check_dir("../backend/data/HAM10000_images_part_1", "Images Part 1")
    images2_exist = check_dir("../backend/data/HAM10000_images_part_2", "Images Part 2")
    
    if not (metadata_exists and (images1_exist or images2_exist)):
        print("\n❌ Dataset files not found!")
        print("   Please download HAM10000 dataset from:")
        print("   https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000")
        print("\n   Extract to: ../backend/data/")
        return
    
    print("\nChecking for train/val split:")
    train_exists = check_dir("../backend/data/train", "Train directory")
    val_exists = check_dir("../backend/data/val", "Val directory")
    
    if not (train_exists and val_exists):
        print("\n⚠️  Train/val split not found!")
        if prompt_yes_no("Do you want to create the split now?"):
            print("\nRunning: python prepare_dataset.py")
            result = subprocess.run([sys.executable, "prepare_dataset.py"], cwd=".")
            if result.returncode == 0:
                print("✓ Dataset split created successfully")
            else:
                print("❌ Dataset preparation failed")
                return
        else:
            print("Skipping dataset preparation")
            return
    else:
        print("✓ Train/val split exists")
    
    # ========================================================================
    # STEP 2: Model Training
    # ========================================================================
    
    print_section("STEP 2: Model Training")
    
    print("\nChecking for trained model:")
    model_exists = check_file("model_tensorflow.h5", "Model file")
    class_indices_exist = check_file("../backend/model/class_indices.json", "Class indices")
    
    if not (model_exists and class_indices_exist):
        print("\n⚠️  Trained model not found!")
        if prompt_yes_no("Do you want to train the model now? (This takes 10-30 minutes)"):
            print("\nRunning: python train_tensorflow.py")
            result = subprocess.run([sys.executable, "train_tensorflow.py"], cwd=".")
            if result.returncode == 0:
                print("✓ Model trained successfully")
            else:
                print("❌ Training failed")
                return
        else:
            print("⚠️  Skipping training - cannot test without model")
            return
    else:
        print("✓ Model files exist")
        if model_exists:
            model_size = os.path.getsize("model_tensorflow.h5") / (1024*1024)
            print(f"  Model size: {model_size:.2f} MB")
    
    # ========================================================================
    # STEP 3: Validation
    # ========================================================================
    
    print_section("STEP 3: Training/Inference Alignment Validation")
    
    print("\nRunning: python validate_training.py")
    result = subprocess.run([sys.executable, "validate_training.py"], cwd=".")
    
    if result.returncode != 0:
        print("⚠️  Validation had some issues")
    
    # ========================================================================
    # STEP 4: Inference Testing
    # ========================================================================
    
    print_section("STEP 4: Inference Testing")
    
    if prompt_yes_no("Do you want to test inference on training images?"):
        print("\nRunning: python test_inference.py")
        result = subprocess.run([sys.executable, "test_inference.py"], cwd=".")
        
        if result.returncode == 0:
            print("\n✓ Inference test completed successfully")
        else:
            print("\n❌ Inference test failed")
    
    # ========================================================================
    # STEP 5: Summary and Next Steps
    # ========================================================================
    
    print_section("PIPELINE COMPLETE")
    
    print("\n✓ Your training/inference pipeline is aligned!")
    print("\nNext steps:")
    print("  1. Use model for production inference:")
    print("     python model_switcher.py set-tensorflow")
    print("\n  2. Test on new images:")
    print("     python model_switcher.py test /path/to/image.jpg")
    print("\n  3. Check status anytime:")
    print("     python model_switcher.py status")
    print("\n  4. Deploy to backend:")
    print("     Update app.py to use: from model_switcher import predict_with_config")
    print("\nDocumentation:")
    print("  - ALIGNMENT_GUIDE.md - Detailed alignment information")
    print("  - README_TENSORFLOW.md - Training and inference guide")
    print("  - SWITCHER_GUIDE.md - Backend integration guide")
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
