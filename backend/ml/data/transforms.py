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
                    print(f"✅ Máscara creada: {mask_path}")

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
    print("✅ Modelo entrenado y guardado en ml/segmentation/cacao_unet.pth")


# ======================================================
# 🎯 USO DEL MODELO PARA QUITAR FONDO
# ======================================================
def remove_background_ai(image_path: str) -> Image.Image:
    """Quita el fondo usando el modelo IA entrenado (U-Net)."""
    model_path = "ml/segmentation/cacao_unet.pth"
    if not os.path.exists(model_path):
        raise FileNotFoundError("❌ No se encontró el modelo entrenado. Ejecuta train_background_ai() primero.")

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
