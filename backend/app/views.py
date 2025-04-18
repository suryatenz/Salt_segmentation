import os
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
import tensorflow as tf

matplotlib.use('Agg')

def dice_loss(y_true, y_pred):
    smooth = 1.0
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return 1 - ((2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth))

def bce_loss(y_true, y_pred):
    return tf.keras.losses.binary_crossentropy(y_true, y_pred)

def combined_loss(y_true, y_pred):
    return bce_loss(y_true, y_pred) + dice_loss(y_true, y_pred)

MODEL_PATH = os.path.join(
    os.path.dirname(settings.BASE_DIR),
    'model',
    'unet_salt_segmentation.keras'
)
model = load_model(MODEL_PATH, custom_objects={'combined_loss': combined_loss})

def preprocess_image(image):
    image = image.convert("L")
    image = image.resize((128, 128))
    img_arr = np.array(image, dtype=np.float32) / 255.0
    img_arr = np.expand_dims(img_arr, axis=(0, -1))
    return img_arr

@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    if 'image' not in request.FILES:
        return Response({'error': 'No image uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        image_file = request.FILES['image']
        pil_image = Image.open(image_file)
        processed = preprocess_image(pil_image)
        raw_pred = model.predict(processed)
        bin_pred = (raw_pred > 0.5).astype(np.uint8)

        fig, axes = plt.subplots(1, 2, figsize=(6, 3))
        axes[0].imshow(processed[0, :, :, 0], cmap='gray', interpolation='none')
        axes[0].set_title("Input")
        axes[0].axis('off')
        axes[1].imshow(bin_pred[0, :, :, 0], cmap='gray', interpolation='none')
        axes[1].set_title("Prediction")
        axes[1].axis('off')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_plot = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return JsonResponse({
            'message': 'Image processed successfully',
            'result': encoded_plot
        })

    except Exception as e:
        return Response({
            'error': f'Error during prediction: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
