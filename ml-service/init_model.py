"""
Initialize a working model for testing
Creates a basic ResNet50 model with 8 output classes for skin disease classification
"""

import tensorflow as tf
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50
import os
import json

print("Initializing model for skin disease classification...")

# Create output directory if it doesn't exist
os.makedirs(".", exist_ok=True)

# Load pre-trained ResNet50
print("Loading ResNet50 from ImageNet...")
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base model
base_model.trainable = False

# Build new head
inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.3)(x)

# 8 output classes (7 diseases + 1 unknown)
outputs = Dense(8, activation='softmax')(x)

model = Model(inputs, outputs)

# Compile
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"Model created:")
print(f"  Input shape: {model.input_shape}")
print(f"  Output shape: {model.output_shape}")

# Save model
model.save('model_tensorflow.h5')
print("✓ Model saved as model_tensorflow.h5")

# Create class indices
class_indices = {
    "akiec": 0,
    "bcc": 1,
    "bkl": 2,
    "df": 3,
    "mel": 4,
    "nv": 5,
    "vasc": 6,
    "unknown": 7
}

os.makedirs("../backend/model", exist_ok=True)
with open("../backend/model/class_indices.json", "w") as f:
    json.dump(class_indices, f, indent=2)
print("✓ Class indices saved")

print("\n✓ Initialization complete!")
print("Model is ready to use for predictions")
print("Note: Model has not been trained yet - predictions will be random")
print("To improve accuracy, run: python train_with_unknown.py")
