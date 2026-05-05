"""
Enhanced TensorFlow Training Script with "Unknown" Class
Trains ResNet50 on HAM10000 + unknown/non-skin images
8 classes total (7 diseases + 1 unknown)
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
MODEL_PATH = "model_tensorflow_with_unknown.h5"
CLASS_INDICES_PATH = "../backend/model/class_indices.json"
HISTORY_PATH = "training_history.json"

# Class labels (8 classes now)
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

print(f"\n{'='*70}")
print("Enhanced TensorFlow Training - HAM10000 + Unknown Class (8 classes total)")
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
print(f"✓ Available directories: {disease_dirs}\n")

# Check if unknown directory exists
unknown_dir = os.path.join(DATA_DIR, "unknown")
if not os.path.exists(unknown_dir):
    print(f"⚠️  'unknown' directory not found at {unknown_dir}")
    print("   Create this directory and fill it with non-skin images:")
    print("   - Random objects")
    print("   - Indoor scenes")
    print("   - Backgrounds")
    print("   - Any non-skin images")
    print("\n   Training will proceed without 'unknown' class if directory is empty")
    print("   But for safety, create it with some non-skin images!\n")

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

try:
    train_data = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    print(f"✓ Training data loaded from {TRAIN_DIR}")
    print(f"  Total training samples: {train_data.samples}")
    print(f"  Batch size: {BATCH_SIZE}")
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
    print(f"  Total validation samples: {val_data.samples}")
except Exception as e:
    print(f"❌ Error loading validation data: {e}")
    exit(1)

# Get class mapping
class_indices = train_data.class_indices
print(f"\n✓ Class indices from training data:")
for class_name, class_idx in sorted(class_indices.items(), key=lambda x: x[1]):
    print(f"  {class_idx}: {class_name}")

# ============================================================================
# STEP 4: Build Model Architecture
# ============================================================================

print(f"\nSTEP 4: Building ResNet50 transfer learning model...")

# Load pre-trained ResNet50
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base model weights initially
base_model.trainable = False

print("✓ ResNet50 base model loaded (weights frozen)")

# Build custom layers on top
inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.3)(x)

# Output layer (number of classes)
num_classes = len(class_indices)
outputs = Dense(num_classes, activation='softmax')(x)

model = Model(inputs, outputs)

print(f"✓ Model architecture built")
print(f"  Input shape: {model.input_shape}")
print(f"  Output shape: {model.output_shape}")
print(f"  Number of classes: {num_classes}")
print(f"  Total trainable params: {model.count_params():,}")

# Compile model
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("✓ Model compiled with Adam optimizer")

# ============================================================================
# STEP 5: Train Model with Callbacks
# ============================================================================

print(f"\nSTEP 5: Training model for {EPOCHS} epochs...")

# Callbacks
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=2,
    min_lr=1e-7,
    verbose=1
)

model_checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

# Train
history = model.fit(
    train_data,
    epochs=EPOCHS,
    validation_data=val_data,
    callbacks=[early_stopping, reduce_lr, model_checkpoint],
    verbose=1
)

print("✓ Training complete!")

# ============================================================================
# STEP 6: Fine-tune with Base Model Unfrozen
# ============================================================================

print(f"\nSTEP 6: Fine-tuning last 50 layers...")

# Unfreeze last 50 layers of base model
base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

# Compile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE / 10),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("✓ Last 50 layers unfrozen for fine-tuning")

# Fine-tune
history_finetuned = model.fit(
    train_data,
    epochs=20,
    validation_data=val_data,
    callbacks=[early_stopping, reduce_lr, model_checkpoint],
    verbose=1
)

print("✓ Fine-tuning complete!")

# ============================================================================
# STEP 7: Save Model and Class Indices
# ============================================================================

print(f"\nSTEP 7: Saving model and metadata...")

# Save model
model.save(MODEL_PATH, save_format='h5')
print(f"✓ Model saved to {MODEL_PATH}")

model_size = os.path.getsize(MODEL_PATH) / (1024*1024)
print(f"  Model size: {model_size:.2f} MB")

# Save class indices
os.makedirs(os.path.dirname(CLASS_INDICES_PATH), exist_ok=True)
with open(CLASS_INDICES_PATH, 'w') as f:
    json.dump(class_indices, f, indent=2)
print(f"✓ Class indices saved to {CLASS_INDICES_PATH}")

# Save training history
history_dict = {
    'accuracy': [float(x) for x in history.history.get('accuracy', [])],
    'loss': [float(x) for x in history.history.get('loss', [])],
    'val_accuracy': [float(x) for x in history.history.get('val_accuracy', [])],
    'val_loss': [float(x) for x in history.history.get('val_loss', [])],
    'epochs': len(history.history.get('loss', [])),
    'num_classes': num_classes,
    'class_labels': CLASS_LABELS
}

with open(HISTORY_PATH, 'w') as f:
    json.dump(history_dict, f, indent=2)
print(f"✓ Training history saved to {HISTORY_PATH}")

# ============================================================================
# STEP 8: Print Summary
# ============================================================================

print(f"\n{'='*70}")
print("TRAINING SUMMARY")
print(f"{'='*70}")
print(f"Model: ResNet50 with custom head (8 classes)")
print(f"Classes: {', '.join(sorted(class_indices.keys()))}")
print(f"Model file: {MODEL_PATH} ({model_size:.2f} MB)")
print(f"Class indices: {CLASS_INDICES_PATH}")
print(f"Training history: {HISTORY_PATH}")
print(f"\nFinal metrics:")
print(f"  Training accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"  Training loss: {history.history['loss'][-1]:.4f}")
print(f"  Validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
print(f"  Validation loss: {history.history['val_loss'][-1]:.4f}")
print(f"\n{'='*70}\n")

print("✓ Model trained successfully!")
print(f"\nNext steps:")
print(f"1. Verify model with: python test_inference.py")
print(f"2. Deploy with: python model_switcher.py test /path/to/image.jpg")
print(f"3. Update backend to use: model_tensorflow_with_unknown.h5\n")
