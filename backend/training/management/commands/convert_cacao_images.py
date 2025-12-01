from __future__ import annotations

"""
Comando Django:
  Convierte imágenes para entrenamiento:
   - BMP -> JPG (en media/cacao_images/converted_jpg)
   - JPG -> PNG segmentado (en media/cacao_images/processed)

Uso:
  python manage.py convert_cacao_images --limit 0
  python manage.py convert_cacao_images --only bmp   # solo BMP->JPG
  python manage.py convert_cacao_images --only png   # solo JPG->PNG (segmentado)
"""

import io
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand

from ml.utils.logs import get_ml_logger
from ml.utils.io import ensure_dir_exists, save_image
from ml.utils.paths import (
    get_raw_images_dir,
    get_converted_jpg_dir,
    get_processed_images_dir,
)
from ml.segmentation.processor import convert_bmp_to_jpg, segment_and_crop_cacao_bean


logger = get_ml_logger("cacaoscan.management.convert_cacao_images")


class Command(BaseCommand):
    help = "Convierte imágenes BMP->JPG y JPG->PNG (segmentado) para entrenamiento"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0, help="Límite de imágenes a procesar (0=sin límite)")
        parser.add_argument("--only", type=str, choices=["bmp", "png", "all"], default="all",
                            help="Etapa a ejecutar: bmp (BMP->JPG), png (JPG->PNG), all")

    def handle(self, *args, **options):
        limit = options["limit"]
        only = options["only"]

        raw_dir = ensure_dir_exists(get_raw_images_dir())
        jpg_dir = ensure_dir_exists(get_converted_jpg_dir())
        png_dir = ensure_dir_exists(get_processed_images_dir())

        processed = 0

        if only in ("bmp", "all"):
            processed += self._convert_bmp_to_jpg(raw_dir, jpg_dir, limit)

        if only in ("png", "all"):
            processed += self._convert_to_png_segmented(raw_dir, jpg_dir, png_dir, limit)

        self.stdout.write(self.style.SUCCESS(f"Procesamiento completado. Archivos procesados: {processed}"))

    def _process_files(
        self,
        files: list[Path],
        process_func,
        output_dir: Path,
        output_format: str,
        output_extension: str,
        error_prefix: str,
        notice_message: str,
        limit: int
    ) -> int:
        """Procesa archivos con una función de conversión común."""
        self.stdout.write(self.style.NOTICE(notice_message))
        if output_format == "PNG":
            self.stdout.write(self.style.NOTICE(f"Guardando {output_format} en: {output_dir.absolute()}"))
        
        processed = 0
        file_limit = None if limit == 0 else limit
        for file_path in files[:file_limit]:
            result, meta = process_func(file_path)
            if not meta.get("success") or result is None:
                logger.error(f"{error_prefix} {file_path.name}: {meta.get('error')}")
                continue
            out_path = output_dir / f"{file_path.stem}{output_extension}"
            save_image(result, out_path, format=output_format)
            if output_format == "PNG":
                self.stdout.write(f"  ✓ Guardado: {out_path.name}")
            processed += 1
        return processed

    def _convert_bmp_to_jpg(self, raw_dir: Path, jpg_dir: Path, limit: int) -> int:
        """Convierte archivos BMP a JPG."""
        bmp_files = list(raw_dir.glob("*.bmp"))
        return self._process_files(
            files=bmp_files,
            process_func=convert_bmp_to_jpg,
            output_dir=jpg_dir,
            output_format="JPEG",
            output_extension=".jpg",
            error_prefix="Fallo BMP->JPG",
            notice_message=f"BMP encontrados: {len(bmp_files)}",
            limit=limit
        )

    def _convert_to_png_segmented(self, raw_dir: Path, jpg_dir: Path, png_dir: Path, limit: int) -> int:
        """Convierte imágenes a PNG segmentadas."""
        sources = self._get_image_sources(raw_dir, jpg_dir)
        return self._process_files(
            files=sources,
            process_func=segment_and_crop_cacao_bean,
            output_dir=png_dir,
            output_format="PNG",
            output_extension=".png",
            error_prefix="Fallo JPG->PNG",
            notice_message=f"Imágenes a segmentar (jpg/jpeg/png): {len(sources)}",
            limit=limit
        )

    def _get_image_sources(self, raw_dir, jpg_dir):
        """Obtiene las fuentes de imágenes para segmentar."""
        return (
            list(raw_dir.glob("*.jpg")) +
            list(raw_dir.glob("*.jpeg")) +
            list(raw_dir.glob("*.png")) +
            list(jpg_dir.glob("*.jpg")) +
            list(jpg_dir.glob("*.jpeg"))
        )


