"""
TensorFlow Training Script for HAM10000 Skin Disease Classification
Implements transfer learning with ResNet50 on HAM10000 dataset
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import os
import json
import numpy as np
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Dataset configuration
DATA_DIR = "../backend/data"
TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "val")

# Image configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001

# Model configuration
MODEL_PATH = "model_tensorflow.h5"
CLASS_INDICES_PATH = "../backend/model/class_indices.json"
HISTORY_PATH = "training_history.json"

# Class labels
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
print("TensorFlow Training Script - HAM10000 Skin Disease Classification")
print(f"{'='*70}\n")

# ============================================================================
# STEP 1: Check Dataset Structure
# ============================================================================

print("STEP 1: Checking dataset structure...")

if not os.path.exists(DATA_DIR):
    print(f"❌ Data directory not found: {DATA_DIR}")
    print("   Please ensure HAM10000 dataset is in the data/ folder")
    exit(1)

print(f"✓ Data directory exists: {DATA_DIR}")

# List available directories
data_contents = os.listdir(DATA_DIR)
print(f"✓ Contents: {data_contents}")

# Check for disease subdirectories
disease_dirs = [d for d in data_contents if os.path.isdir(os.path.join(DATA_DIR, d))]
print(f"✓ Disease directories found: {disease_dirs}\n")

# ============================================================================
# STEP 2: Data Preprocessing & Augmentation
# ============================================================================

print("STEP 2: Setting up data preprocessing...")

# Training data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    shear_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    fill_mode='nearest'
)

# Validation data (no augmentation, only rescaling)
val_datagen = ImageDataGenerator(rescale=1./255)

print("✓ Data augmentation configured")

# ============================================================================
# STEP 3: Load Data from Directory Structure
# ============================================================================

print("\nSTEP 3: Loading training data...")

# Check if we should use HAM10000 images or create train/val split
if os.path.exists(TRAIN_DIR):
    # Load from existing train/val split
    try:
        train_data = train_datagen.flow_from_directory(
            TRAIN_DIR,
            target_size=IMG_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            shuffle=True
        )
        print(f"✓ Training data loaded from {TRAIN_DIR}")
        print(f"  - Samples: {train_data.samples}")
        print(f"\n=== CLASS INDICES (TRAINING) ===")
        for class_name, class_idx in sorted(train_data.class_indices.items(), key=lambda x: x[1]):
            print(f"  {class_idx}: {class_name:8} → {CLASS_LABELS.get(class_name, class_name)}")
        print(f"====================================\n")
    except Exception as e:
        print(f"❌ Error loading training data: {e}")
        exit(1)
    
    print("\nLoading validation data...")
    try:
        val_data = val_datagen.flow_from_directory(
            VAL_DIR,
            target_size=IMG_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            shuffle=False
        )
        print(f"✓ Validation data loaded from {VAL_DIR}")
        print(f"  - Samples: {val_data.samples}")
    except Exception as e:
        print(f"❌ Error loading validation data: {e}")
        exit(1)
else:
    print(f"⚠️  Train/Val directories not found at:")
    print(f"   - Train: {TRAIN_DIR}")
    print(f"   - Val: {VAL_DIR}")
    print("   Creating a simple train/val split from available images...")
    
    # This is a fallback - you would need to implement your own split logic here
    print("❌ Please prepare train/ and val/ directories in the data/ folder")
    exit(1)

num_classes = len(train_data.class_indices)
print(f"\n✓ Number of classes: {num_classes}")

# ============================================================================
# STEP 4: Build Model (Transfer Learning)
# ============================================================================

print("\nSTEP 4: Building model with transfer learning...")
print("Using ResNet50 pre-trained on ImageNet")

# Load pre-trained ResNet50
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base layers (transfer learning)
base_model.trainable = False
print(f"✓ Base model layers frozen: {len(base_model.layers)} layers")

# Build custom top layers
inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.3)(x)
outputs = Dense(num_classes, activation='softmax')(x)

model = Model(inputs, outputs)

print(f"✓ Model architecture:")
print(f"  - Input: (224, 224, 3)")
print(f"  - Base: ResNet50 (frozen)")
print(f"  - Dense layers: 512 → 256")
print(f"  - Output: {num_classes} (softmax)")
print(f"  - Total parameters: {model.count_params():,}")

# ============================================================================
# STEP 5: Compile Model
# ============================================================================

print("\nSTEP 5: Compiling model...")

optimizer = Adam(learning_rate=LEARNING_RATE)
model.compile(
    optimizer=optimizer,
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"✓ Model compiled")
print(f"  - Optimizer: Adam (lr={LEARNING_RATE})")
print(f"  - Loss: categorical_crossentropy")
print(f"  - Metrics: accuracy")

# ============================================================================
# STEP 6: Setup Callbacks
# ============================================================================

print("\nSTEP 6: Setting up training callbacks...")

callbacks = [
    # Save best model
    ModelCheckpoint(
        MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    # Early stopping
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    # Reduce learning rate on plateau
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

print("✓ Callbacks configured:")
print("  - ModelCheckpoint: Save best model")
print("  - EarlyStopping: Stop if no improvement for 10 epochs")
print("  - ReduceLROnPlateau: Reduce LR if loss plateaus")

# ============================================================================
# STEP 7: Train Model
# ============================================================================

print(f"\nSTEP 7: Training model for {EPOCHS} epochs...")
print(f"{'='*70}\n")

history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
    callbacks=callbacks,
    verbose=1
)

print(f"\n{'='*70}")
print("✓ Training complete!")

# ============================================================================
# STEP 8: Evaluate Model
# ============================================================================

print("\nSTEP 8: Evaluating model on validation set...")

val_loss, val_accuracy = model.evaluate(val_data, verbose=0)

print(f"✓ Validation Results:")
print(f"  - Loss: {val_loss:.4f}")
print(f"  - Accuracy: {val_accuracy*100:.2f}%")

# ============================================================================
# STEP 9: Save Model and Metadata
# ============================================================================

print("\nSTEP 9: Saving model and metadata...")

# Save the model
model.save(MODEL_PATH, save_format='h5')
print(f"✓ Model saved to: {MODEL_PATH}")

# Save class indices if not already saved
if not os.path.exists(os.path.dirname(CLASS_INDICES_PATH)):
    os.makedirs(os.path.dirname(CLASS_INDICES_PATH), exist_ok=True)

class_indices = train_data.class_indices
with open(CLASS_INDICES_PATH, 'w') as f:
    json.dump(class_indices, f, indent=2)
print(f"✓ Class indices saved to: {CLASS_INDICES_PATH}")

# Save training history
history_dict = {
    'loss': history.history['loss'],
    'accuracy': history.history['accuracy'],
    'val_loss': history.history['val_loss'],
    'val_accuracy': history.history['val_accuracy']
}
with open(HISTORY_PATH, 'w') as f:
    json.dump(history_dict, f, indent=2)
print(f"✓ Training history saved to: {HISTORY_PATH}")

# ============================================================================
# STEP 10: Fine-tune (Optional)
# ============================================================================

print("\nSTEP 10: Fine-tuning model...")
print("Unfreezing last 50 base layers for fine-tuning...")

# Unfreeze last layers of base model
base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

# Recompile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE / 10),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("✓ Model recompiled for fine-tuning")

# Fine-tune for additional epochs
print(f"Fine-tuning for 10 additional epochs...\n")

fine_tune_history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks,
    verbose=1
)

# Save fine-tuned model
model.save(MODEL_PATH, save_format='h5')
print(f"\n✓ Fine-tuned model saved to: {MODEL_PATH}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"\n{'='*70}")
print("TRAINING SUMMARY")
print(f"{'='*70}")
print(f"Model saved: {MODEL_PATH}")
print(f"Classes: {list(class_indices.keys())}")
print(f"Number of classes: {len(class_indices)}")
print(f"Final validation accuracy: {val_accuracy*100:.2f}%")
print(f"\nTo use this model for inference, update model.py to load:")
print(f"  model = tf.keras.models.load_model('{MODEL_PATH}')")
print(f"{'='*70}\n")
