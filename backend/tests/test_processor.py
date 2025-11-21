import os
from pathlib import Path
from PIL import Image
import numpy as np
import pytest

# Importa la función principal desde tu módulo
from ml.segmentation.processor import segment_and_crop_cacao_bean


@pytest.mark.unit
def test_segment_and_crop_cacao_bean_creates_png(tmp_path):
    """
    🧪 Test IA: segmenta y recorta una imagen de cacao.
    Verifica que:
    1️⃣ El archivo existe.
    2️⃣ El resultado sea PNG.
    3️⃣ Contenga canal alfa (transparencia).
    """

    # 🖼️ Ruta de la imagen de prueba
    input_image = os.path.abspath("media/datasets/pruebas2.jpg.jpg")
    assert os.path.exists(input_image), f"La imagen de prueba no existe: {input_image}"

    # 🚀 Ejecutar el procesamiento
    output_path = segment_and_crop_cacao_bean(input_image)

    # ✅ Validaciones de salida
    assert output_path.endswith(".png"), "El archivo resultante no es PNG"
    assert os.path.exists(output_path), "El archivo de salida no fue creado"

    # 🔍 Validar que tenga canal alfa (RGBA)
    img = Image.open(output_path)
    assert img.mode == "RGBA", f"El modo de imagen no es RGBA, es {img.mode}"

    # 🩸 Comprobar que hay transparencia real (no fondo sólido)
    alpha_channel = np.array(img.split()[-1])
    transparent_ratio = np.mean(alpha_channel < 250)  # % de píxeles transparentes
    assert transparent_ratio > 0.1, "La imagen no presenta fondo eliminado adecuadamente"

    # 🧼 Limpieza automática del archivo de salida
    os.remove(output_path)


def test_processor_handles_missing_file():
    """
    🧱 Test de robustez: el procesador debe lanzar error si el archivo no existe.
    """
    with pytest.raises(FileNotFoundError):
        segment_and_crop_cacao_bean("media/datasets/inexistente.jpg")
