"""
Cargador y validador del dataset de cacao.
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from ..utils.paths import (
    get_dataset_csv_path,
    get_raw_images_dir,
    get_missing_ids_log_path,
    ensure_dir_exists
)
from ..utils.io import write_log, get_file_timestamp


logger = logging.getLogger("cacaoscan.ml.data")


class CacaoDatasetLoader:
    """Cargador y validador del dataset de cacao."""
    
    def __init__(self):
        self.csv_path = get_dataset_csv_path()
        self.raw_images_dir = get_raw_images_dir()
        self.missing_log_path = get_missing_ids_log_path()
        
        # Asegurar que los directorios existen
        ensure_dir_exists(self.raw_images_dir)
        ensure_dir_exists(self.missing_log_path.parent)
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Carga el dataset CSV y valida los tipos de datos.
        
        Returns:
            DataFrame con el dataset cargado y validado
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Dataset CSV no encontrado en {self.csv_path}")
        
        logger.info(f"Cargando dataset desde {self.csv_path}")
        
        # Cargar CSV
        df = pd.read_csv(self.csv_path)
        
        # Validar columnas requeridas
        required_columns = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Columnas faltantes en el dataset: {missing_columns}")
        
        # Convertir tipos de datos
        df['ID'] = df['ID'].astype(int)
        df['ALTO'] = pd.to_numeric(df['ALTO'], errors='coerce')
        df['ANCHO'] = pd.to_numeric(df['ANCHO'], errors='coerce')
        df['GROSOR'] = pd.to_numeric(df['GROSOR'], errors='coerce')
        df['PESO'] = pd.to_numeric(df['PESO'], errors='coerce')
        
        # Eliminar filas con valores nulos
        initial_count = len(df)
        df = df.dropna()
        final_count = len(df)
        
        if initial_count != final_count:
            logger.warning(f"Eliminadas {initial_count - final_count} filas con valores nulos")
        
        logger.info(f"Dataset cargado: {final_count} registros válidos")
        return df
    
    def validate_images_exist(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[int]]:
        """
        Valida que las imágenes correspondientes a los IDs existan.
        
        Args:
            df: DataFrame con los datos del dataset
            
        Returns:
            Tuple con (DataFrame filtrado, Lista de IDs faltantes)
        """
        logger.info("Validando existencia de imágenes...")
        
        missing_ids = []
        valid_records = []
        
        for _, row in df.iterrows():
            image_id = row['ID']
            image_path = self.raw_images_dir / f"{image_id}.bmp"
            
            if image_path.exists():
                valid_records.append(row)
            else:
                missing_ids.append(image_id)
                logger.warning(f"Imagen faltante para ID {image_id}")
        
        # Guardar log de IDs faltantes
        if missing_ids:
            log_message = f"IDs con imágenes faltantes: {missing_ids}"
            write_log(self.missing_log_path, log_message)
            logger.warning(f"Guardado log de {len(missing_ids)} IDs faltantes en {self.missing_log_path}")
        
        valid_df = pd.DataFrame(valid_records)
        logger.info(f"Validación completada: {len(valid_df)} registros válidos, {len(missing_ids)} faltantes")
        
        return valid_df, missing_ids
    
    def get_valid_records(self) -> List[Dict]:
        """
        Obtiene la lista de registros válidos con rutas de imágenes.
        
        Returns:
            Lista de diccionarios con información de cada registro válido
        """
        # Cargar y validar dataset
        df = self.load_dataset()
        valid_df, missing_ids = self.validate_images_exist(df)
        
        # Crear lista de registros válidos
        valid_records = []
        
        for _, row in valid_df.iterrows():
            image_id = row['ID']
            raw_path = self.raw_images_dir / f"{image_id}.bmp"
            
            record = {
                'id': image_id,
                'alto': row['ALTO'],
                'ancho': row['ANCHO'],
                'grosor': row['GROSOR'],
                'peso': row['PESO'],
                'raw_image_path': raw_path,
                'crop_image_path': None,  # Se establecerá después del procesamiento
                'mask_image_path': None,  # Se establecerá después del procesamiento
                'timestamp': get_file_timestamp(raw_path)
            }
            valid_records.append(record)
        
        logger.info(f"Generados {len(valid_records)} registros válidos")
        return valid_records
    
    def get_dataset_stats(self) -> Dict:
        """
        Obtiene estadísticas del dataset.
        
        Returns:
            Diccionario con estadísticas del dataset
        """
        try:
            df = self.load_dataset()
            valid_df, missing_ids = self.validate_images_exist(df)
            
            stats = {
                'total_records': len(df),
                'valid_records': len(valid_df),
                'missing_images': len(missing_ids),
                'missing_ids': missing_ids,
                'dimensions_stats': {
                    'alto': {
                        'min': valid_df['ALTO'].min(),
                        'max': valid_df['ALTO'].max(),
                        'mean': valid_df['ALTO'].mean(),
                        'std': valid_df['ALTO'].std()
                    },
                    'ancho': {
                        'min': valid_df['ANCHO'].min(),
                        'max': valid_df['ANCHO'].max(),
                        'mean': valid_df['ANCHO'].mean(),
                        'std': valid_df['ANCHO'].std()
                    },
                    'grosor': {
                        'min': valid_df['GROSOR'].min(),
                        'max': valid_df['GROSOR'].max(),
                        'mean': valid_df['GROSOR'].mean(),
                        'std': valid_df['GROSOR'].std()
                    },
                    'peso': {
                        'min': valid_df['PESO'].min(),
                        'max': valid_df['PESO'].max(),
                        'mean': valid_df['PESO'].mean(),
                        'std': valid_df['PESO'].std()
                    }
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas del dataset: {e}")
            return {}


def load_cacao_dataset() -> Tuple[pd.DataFrame, List[int]]:
    """
    Función de conveniencia para cargar el dataset y validar imágenes.
    
    Returns:
        Tuple con (DataFrame válido, Lista de IDs faltantes)
    """
    loader = CacaoDatasetLoader()
    df = loader.load_dataset()
    return loader.validate_images_exist(df)


def get_valid_cacao_records() -> List[Dict]:
    """
    Función de conveniencia para obtener registros válidos.
    
    Returns:
        Lista de registros válidos con información completa
    """
    loader = CacaoDatasetLoader()
    return loader.get_valid_records()
