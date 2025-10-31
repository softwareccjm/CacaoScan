import os
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms as T
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# ======================================================
# 🧠 MODELO: U-Net ligero para segmentación de fondo
# ======================================================
class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

class UNet(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super().__init__()
        self.down1 = DoubleConv(n_channels, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.bottom = DoubleConv(128, 256)
        self.up1 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.conv1 = DoubleConv(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.conv2 = DoubleConv(128, 64)
        self.final = nn.Conv2d(64, n_classes, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x1 = self.down1(x)
        x2 = self.pool1(x1)
        x3 = self.down2(x2)
        x4 = self.pool2(x3)
        x5 = self.bottom(x4)
        x = self.up1(x5)
        x = torch.cat([x, x3], dim=1)
        x = self.conv1(x)
        x = self.up2(x)
        x = torch.cat([x, x1], dim=1)
        x = self.conv2(x)
        x = self.final(x)
        return self.sigmoid(x)


# ======================================================
# 📦 DATASET AUTOMÁTICO (crea máscaras si no existen)
# ======================================================
class CacaoDataset(Dataset):
    def __init__(self, img_dir, mask_dir, transform=None, auto_generate=False):
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.transform = transform
        self.images = os.listdir(img_dir)
        self.auto_generate = auto_generate

        if auto_generate:
            os.makedirs(mask_dir, exist_ok=True)
            for img in self.images:
                mask_path = os.path.join(mask_dir, img.replace(".jpg", ".png"))
                if not os.path.exists(mask_path):
                    mask = self._auto_mask(os.path.join(img_dir, img))
                    cv2.imwrite(mask_path, mask)
                    print(f"[OK] Máscara creada: {mask_path}")

    def _auto_mask(self, image_path):
        """Usa OpenCV (grabCut) para generar máscara base automática."""
        img = cv2.imread(image_path)
        mask = np.zeros(img.shape[:2], np.uint8)
        rect = (10, 10, img.shape[1]-20, img.shape[0]-20)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 10, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8') * 255
        return mask2

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.images[idx])
        mask_path = os.path.join(self.mask_dir, self.images[idx].replace(".jpg", ".png"))
        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask


# ======================================================
# ⚙️ ENTRENAMIENTO DEL MODELO
# ======================================================
def train_background_ai(image_dir="ml/data/dataset/images", mask_dir="ml/data/dataset/masks", epochs=10):
    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor(),
    ])

    dataset = CacaoDataset(image_dir, mask_dir, transform, auto_generate=True)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = UNet().to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    for epoch in range(epochs):
        for imgs, masks in loader:
            imgs, masks = imgs.to(device), masks.to(device)
            preds = model(imgs)
            loss = criterion(preds, masks)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/{epochs} | Loss: {loss.item():.4f}")

    os.makedirs("ml/segmentation", exist_ok=True)
    torch.save(model.state_dict(), "ml/segmentation/cacao_unet.pth")
    print("[OK] Modelo entrenado y guardado en ml/segmentation/cacao_unet.pth")


# ======================================================
# 🎯 USO DEL MODELO PARA QUITAR FONDO
# ======================================================
def remove_background_ai(image_path: str) -> Image.Image:
    """Quita el fondo usando el modelo IA entrenado (U-Net)."""
    model_path = "ml/segmentation/cacao_unet.pth"
    if not os.path.exists(model_path):
        raise FileNotFoundError("[ERROR] No se encontró el modelo entrenado. Ejecuta train_background_ai() primero.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = UNet().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    img = Image.open(image_path).convert("RGB")
    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor()
    ])
    tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        mask = model(tensor)[0][0].cpu().numpy()

    mask = (mask - mask.min()) / (mask.max() - mask.min())
    mask = cv2.resize(mask, img.size)
    rgba = np.dstack((np.array(img), (mask * 255).astype(np.uint8)))
    return Image.fromarray(rgba, "RGBA")


def resize_crop_to_square(
    image_rgba: np.ndarray,
    target_size: int = 512,
    fill_color: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> np.ndarray:
    """
    Redimensiona una imagen RGBA manteniendo proporción y la centra
    en un lienzo cuadrado target_size x target_size con fill_color.
    """
    if image_rgba is None:
        raise ValueError("image_rgba cannot be None")

    h, w = image_rgba.shape[:2]
    scale = min(target_size / w, target_size / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = cv2.resize(image_rgba, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((target_size, target_size, 4), dtype=np.uint8)
    canvas[:, :, 0] = fill_color[0]
    canvas[:, :, 1] = fill_color[1]
    canvas[:, :, 2] = fill_color[2]
    canvas[:, :, 3] = fill_color[3]

    y_off = (target_size - new_h) // 2
    x_off = (target_size - new_w) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
    return canvas


def resize_with_padding(
    image: np.ndarray,
    target_size: tuple[int, int] = (640, 640),
    fill_color: tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """
    Redimensiona manteniendo proporción y rellena hasta target_size (alto, ancho).
    Acepta imagen GRAY/RGB/RGBA.
    """
    if image is None:
        raise ValueError("image cannot be None")

    h, w = image.shape[:2]
    th, tw = target_size
    scale = min(th / h, tw / w)
    new_h, new_w = int(round(h * scale)), int(round(w * scale))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    if image.ndim == 2:
        canvas = np.full((th, tw), fill_color[0], dtype=resized.dtype)
        y0 = (th - new_h) // 2
        x0 = (tw - new_w) // 2
        canvas[y0:y0+new_h, x0:x0+new_w] = resized
        return canvas

    c = image.shape[2]
    if c == 3:
        canvas = np.zeros((th, tw, 3), dtype=resized.dtype)
        canvas[:, :, 0] = fill_color[0]
        canvas[:, :, 1] = fill_color[1]
        canvas[:, :, 2] = fill_color[2]
    else:
        # RGBA
        canvas = np.zeros((th, tw, 4), dtype=resized.dtype)
        canvas[:, :, 0] = fill_color[0]
        canvas[:, :, 1] = fill_color[1]
        canvas[:, :, 2] = fill_color[2]
        canvas[:, :, 3] = fill_color[3] if len(fill_color) == 4 else 0

    y0 = (th - new_h) // 2
    x0 = (tw - new_w) // 2
    canvas[y0:y0+new_h, x0:x0+new_w] = resized
    return canvas


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normaliza una imagen a rango [0, 1] en float32."""
    if image is None:
        raise ValueError("image cannot be None")
    img = image.astype(np.float32)
    if img.max() > 1.0:
        img = img / 255.0
    return img


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """Desnormaliza una imagen de [0, 1] a uint8 [0, 255]."""
    if image is None:
        raise ValueError("image cannot be None")
    img = np.clip(image, 0.0, 1.0)
    return (img * 255.0).astype(np.uint8)


def validate_crop_quality(image_rgb: np.ndarray, mask: np.ndarray, min_aspect_ratio: float = 0.1, max_aspect_ratio: float = 10.0, min_area: int = 100) -> bool:
    """
    Valida que el recorte tenga proporciones razonables.
    
    Args:
        image_rgb: Imagen RGB (H, W, 3)
        mask: Máscara binaria (H, W) con valores 0-255
        min_aspect_ratio: Ratio mínimo permitido (ancho/alto) - más permisivo para granos variados
        max_aspect_ratio: Ratio máximo permitido (ancho/alto) - más permisivo para granos variados
        min_area: Área mínima en píxeles del objeto detectado
        
    Returns:
        True si el recorte es válido, False en caso contrario
    """
    if image_rgb is None or mask is None:
        return False
    
    # Convertir máscara a binaria si es necesario
    if mask.dtype != np.uint8 or mask.max() > 1:
        mask_binary = (mask > 128).astype(np.uint8)
    else:
        mask_binary = mask
    
    # Encontrar bounding box del objeto
    contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False
    
    # Usar el contorno más grande
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Validar que el recorte tenga un área mínima (más flexible)
    area = w * h
    if area < min_area:
        return False
    
    # Validar dimensiones mínimas (más flexible)
    if w < 5 or h < 5:
        return False
    
    # Calcular aspect ratio
    aspect_ratio = w / h if h > 0 else 0
    
    # Validar aspect ratio con rangos más permisivos para granos de cacao
    # Los granos pueden ser redondos (ratio ~1.0) o más alargados
    if aspect_ratio < min_aspect_ratio or aspect_ratio > max_aspect_ratio:
        # Log para debug (opcional, solo si hay problemas)
        return False
    
    return True


def create_transparent_crop(image_rgb: np.ndarray, mask: np.ndarray, padding: int = 10, crop_only: bool = False) -> np.ndarray:
    """
    Crea una imagen con fondo transparente usando una máscara.
    
    Args:
        image_rgb: Imagen RGB (H, W, 3)
        mask: Máscara binaria (H, W) con valores 0-255
        padding: Padding en píxeles alrededor del objeto (si crop_only=True)
        crop_only: Si True, recorta solo el bounding box. Si False, usa toda la imagen.
    
    Returns:
        Imagen RGBA con fondo transparente (H, W, 4)
    """
    if image_rgb is None or mask is None:
        raise ValueError("image_rgb y mask no pueden ser None")
    
    # Asegurar que la máscara tenga el mismo tamaño que la imagen
    if mask.shape[:2] != image_rgb.shape[:2]:
        mask = cv2.resize(mask, (image_rgb.shape[1], image_rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
    
    # Convertir máscara a binaria si es necesario
    if mask.dtype != np.uint8:
        if mask.max() <= 1.0:
            mask_binary = (mask * 255).astype(np.uint8)
        else:
            mask_binary = mask.astype(np.uint8)
    else:
        mask_binary = mask
    
    # Normalizar a 0-255 si es necesario
    if mask_binary.max() <= 1:
        mask_binary = (mask_binary * 255).astype(np.uint8)
    else:
        mask_binary = np.clip(mask_binary, 0, 255).astype(np.uint8)
    
    # Normalizar máscara a [0, 1] para alpha
    alpha = (mask_binary / 255.0).astype(np.float32)
    
    if crop_only:
        # Recortar solo el bounding box del grano - método preciso que elimina bordes blancos
        # 1. Usar la máscara para encontrar píxeles visibles
        _, mask_thresh = cv2.threshold(mask_binary, 127, 255, cv2.THRESH_BINARY)
        
        # 2. Encontrar coordenadas de todos los píxeles visibles (no transparentes)
        coords = np.where(mask_thresh > 0)
        
        if len(coords[0]) == 0:
            # Si no hay píxeles visibles, usar toda la imagen
            bbox = (0, 0, image_rgb.shape[1], image_rgb.shape[0])
        else:
            # 3. Calcular bounding box exacto desde los píxeles visibles (SIN padding para eliminar bordes)
            y_min, y_max = coords[0].min(), coords[0].max()
            x_min, x_max = coords[1].min(), coords[1].max()
            
            # 4. Calcular dimensiones exactas
            w = x_max - x_min + 1
            h = y_max - y_min + 1
            
            # 5. Asegurar que no salimos de los límites de la imagen
            x = max(0, x_min)
            y = max(0, y_min)
            w = min(image_rgb.shape[1] - x, w)
            h = min(image_rgb.shape[0] - y, h)
            
            bbox = (x, y, w, h)
        
        x, y, w, h = bbox
        
        # 6. Recortar imagen y máscara con precisión (mantener calidad original)
        crop_image = image_rgb[y:y+h, x:x+w].copy()  # .copy() para evitar problemas de referencia
        crop_alpha = alpha[y:y+h, x:x+w].copy()
        
        # 7. Crear imagen RGBA recortada con alta calidad
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = crop_image
        
        # 8. Aplicar máscara alpha con umbral para eliminar ruido de fondo
        alpha_uint8 = (crop_alpha * 255).astype(np.uint8)
        # Eliminar píxeles con alpha muy bajo (ruido)
        alpha_uint8[alpha_uint8 < 30] = 0
        rgba[:, :, 3] = alpha_uint8
        
        # 9. Limpieza final: eliminar bordes completamente transparentes
        # Encontrar área real después de aplicar alpha
        final_coords = np.where(alpha_uint8 > 0)
        if len(final_coords[0]) > 0:
            final_y_min, final_y_max = final_coords[0].min(), final_coords[0].max()
            final_x_min, final_x_max = final_coords[1].min(), final_coords[1].max()
            
            # Solo recortar si hay bordes transparentes significativos (>3px)
            if (final_y_min > 3 or final_y_max < h - 3 or final_x_min > 3 or final_x_max < w - 3):
                rgba = rgba[final_y_min:final_y_max+1, final_x_min:final_x_max+1]
    else:
        # Modo nuevo: usar toda la imagen con fondo transparente
        h, w = image_rgb.shape[:2]
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = image_rgb
        rgba[:, :, 3] = (alpha * 255).astype(np.uint8)
    
    return rgba
