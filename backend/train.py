import os
import pandas as pd
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

# Load metadata
metadata_path = os.path.join(DATA_DIR, 'HAM10000_metadata.csv')
if not os.path.exists(metadata_path):
    raise FileNotFoundError('HAM10000_metadata.csv not found in data folder.')

df = pd.read_csv(metadata_path)

# Map image IDs to actual file paths (search in subfolders)
image_paths = []
for root, _, files in os.walk(DATA_DIR):
    for f in files:
        if f.lower().endswith('.jpg'):
            img_id = os.path.splitext(f)[0]
            img_path = os.path.join(root, f)
            image_paths.append((img_id, img_path))
image_dict = dict(image_paths)

df['image_path'] = df['image_id'].map(image_dict)
missing = df['image_path'].isna().sum()
if missing > 0:
    print(f'Warning: {missing} images could not be located on disk.')

df = df.dropna(subset=['image_path']).reset_index(drop=True)

# Split into train/validation (80/20)
train_df = df.sample(frac=0.8, random_state=42)
val_df = df.drop(train_df.index)

# Image generators
train_gen = ImageDataGenerator(
    rescale=1./255,
    horizontal_flip=True,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1
)
val_gen = ImageDataGenerator(rescale=1./255)

train_flow = train_gen.flow_from_dataframe(
    dataframe=train_df,
    x_col='image_path',
    y_col='dx',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=True
)
val_flow = val_gen.flow_from_dataframe(
    dataframe=val_df,
    x_col='image_path',
    y_col='dx',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=False
)

num_classes = train_flow.num_classes
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
for layer in base_model.layers:
    layer.trainable = False
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.2)(x)
output = Dense(num_classes, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

checkpoint_path = os.path.join(MODEL_DIR, 'skin_model.h5')
checkpoint = ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True, mode='max')
early = EarlyStopping(monitor='val_accuracy', patience=3, mode='max', restore_best_weights=True)

model.fit(
    train_flow,
    epochs=5,
    validation_data=val_flow,
    callbacks=[checkpoint, early]
)

# Save class index mapping (string label -> integer index)
class_indices = train_flow.class_indices  # dict label->index
# Invert to index->label for prediction
inv_class_indices = {v: k for k, v in class_indices.items()}
with open(os.path.join(MODEL_DIR, 'class_indices.json'), 'w') as f:
    json.dump(inv_class_indices, f)

print('Training complete. Model saved to', checkpoint_path)
