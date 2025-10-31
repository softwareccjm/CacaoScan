"""
Script de entrenamiento para modelos de regresión de dimensiones de cacao.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging
import json
import time
from datetime import datetime

from ..utils.logs import get_ml_logger
from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from .models import create_model, TARGETS, TARGET_NAMES, get_model_info
from .scalers import CacaoScalers, save_scalers

# Importar Django para usar ModelMetrics
import os
import sys
from pathlib import Path

# Configurar Django
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
django.setup()

from api.models import ModelMetrics, TrainingJob
from django.contrib.auth.models import User


logger = get_ml_logger("cacaoscan.ml.regression")


class RegressionTrainer:
    """Entrenador para modelos de regresión de cacao."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        scalers: CacaoScalers,
        target: str,
        device: torch.device,
        config: Dict
    ):
        """
        Inicializa el entrenador.
        
        Args:
            model: Modelo a entrenar
            train_loader: DataLoader de entrenamiento
            val_loader: DataLoader de validación
            scalers: Escaladores para normalización
            target: Target a entrenar
            device: Dispositivo para entrenamiento
            config: Configuración de entrenamiento
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.scalers = scalers
        self.target = target
        self.device = device
        self.config = config
        
        # Configurar optimizador con mejor configuración
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config.get('learning_rate', 1e-4),
            weight_decay=config.get('weight_decay', 1e-4),
            betas=(0.9, 0.999),
            eps=1e-8,
            amsgrad=False
        )
        
        # Configurar scheduler avanzado (OneCycleLR o CosineAnnealingWarmRestarts)
        scheduler_type = config.get('scheduler_type', 'cosine_warmup')
        epochs = config.get('epochs', 50)
        
        if scheduler_type == 'onecycle':
            # OneCycleLR: muy efectivo para entrenamiento rápido
            self.scheduler = optim.lr_scheduler.OneCycleLR(
                self.optimizer,
                max_lr=config.get('learning_rate', 1e-4) * 10,
                epochs=epochs,
                steps_per_epoch=len(train_loader),
                pct_start=0.3,
                anneal_strategy='cos',
                div_factor=25.0,
                final_div_factor=10000.0
            )
        elif scheduler_type == 'cosine_warmup':
            # CosineAnnealingWarmRestarts: permite restarts para exploración
            self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
                self.optimizer,
                T_0=epochs // 4,  # Restart cada 1/4 de épocas
                T_mult=2,
                eta_min=config.get('min_lr', 1e-7)
            )
        else:
            # CosineAnnealingLR con warmup manual
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=epochs,
                eta_min=config.get('min_lr', 1e-6)
            )
            self.warmup_epochs = config.get('warmup_epochs', 5)
        
        # Criterio de pérdida mejorado (Huber Loss es más robusto que MSE)
        loss_type = config.get('loss_type', 'mse')
        if loss_type == 'huber':
            self.criterion = nn.HuberLoss(delta=1.0)
        elif loss_type == 'smooth_l1':
            self.criterion = nn.SmoothL1Loss()
        elif loss_type == 'mse':
            self.criterion = nn.MSELoss()
        else:
            self.criterion = nn.MSELoss()
        
        # Gradient clipping para estabilidad
        self.max_grad_norm = config.get('max_grad_norm', 1.0)
        
        # Mixed precision training si está disponible
        self.use_amp = config.get('use_amp', False) and hasattr(torch.cuda, 'amp')
        if self.use_amp:
            self.scaler = torch.cuda.amp.GradScaler()
            logger.info("Mixed precision training habilitado")
        
        # Early stopping
        self.early_stopping_patience = config.get('early_stopping_patience', 10)
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.best_model_state = None
        
        # Historial de entrenamiento
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'val_mae': [],
            'val_rmse': [],
            'val_r2': [],
            'learning_rate': []
        }
        
        logger.info(f"Entrenador inicializado para target: {target}")
        logger.info(f"Modelo: {get_model_info(self.model)}")
    
    def train_epoch(self) -> float:
        """Entrena el modelo por una época con mejoras avanzadas."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, (images, targets) in enumerate(self.train_loader):
            images = images.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass con mixed precision si está habilitado
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, targets)
                
                # Backward pass con scaling
                self.scaler.scale(loss).backward()
                
                # Gradient clipping
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                
                # Optimizer step
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                # Forward pass normal
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)
                
                # Backward pass
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                
                # Optimizer step
                self.optimizer.step()
            
            # Update scheduler si es OneCycleLR (se actualiza por step)
            if isinstance(self.scheduler, optim.lr_scheduler.OneCycleLR):
                self.scheduler.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # Log periódico más detallado
            if batch_idx % max(1, len(self.train_loader) // 10) == 0:
                current_lr = self.scheduler.get_last_lr()[0] if not isinstance(self.scheduler, optim.lr_scheduler.OneCycleLR) else self.scheduler.get_last_lr()[0]
                logger.debug(
                    f"Batch {batch_idx}/{len(self.train_loader)} - "
                    f"Loss: {loss.item():.4f}, LR: {current_lr:.2e}"
                )
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate_epoch(self) -> Tuple[float, float, float, float]:
        """
        Valida el modelo por una época.
        
        Returns:
            Tuple con (loss, mae, rmse, r2)
        """
        self.model.eval()
        total_loss = 0.0
        total_mae = 0.0
        total_rmse = 0.0
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for images, targets in self.val_loader:
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)
                
                total_loss += loss.item()
                
                # Convertir a numpy para métricas
                predictions = outputs.cpu().numpy().flatten()
                targets_np = targets.cpu().numpy().flatten()
                
                all_predictions.extend(predictions)
                all_targets.extend(targets_np)
        
        # Calcular métricas
        all_predictions = np.array(all_predictions)
        all_targets = np.array(all_targets)
        
        avg_loss = total_loss / len(self.val_loader)
        mae = np.mean(np.abs(all_predictions - all_targets))
        rmse = np.sqrt(np.mean((all_predictions - all_targets) ** 2))
        
        # R² score
        ss_res = np.sum((all_targets - all_predictions) ** 2)
        ss_tot = np.sum((all_targets - np.mean(all_targets)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return avg_loss, mae, rmse, r2
    
    def train(self) -> Dict[str, List[float]]:
        """
        Entrena el modelo completo.
        
        Returns:
            Historial de entrenamiento
        """
        logger.info(f"Iniciando entrenamiento para {self.target}")
        logger.info(f"Épocas: {self.config['epochs']}, Batch size: {self.config['batch_size']}")
        
        start_time = time.time()
        
        for epoch in range(self.config['epochs']):
            epoch_start = time.time()
            
            # Entrenar
            train_loss = self.train_epoch()
            
            # Validar
            val_loss, val_mae, val_rmse, val_r2 = self.validate_epoch()
            
            # Actualizar scheduler (excepto OneCycleLR que se actualiza por step)
            if not isinstance(self.scheduler, optim.lr_scheduler.OneCycleLR):
                # Warmup manual si no es OneCycleLR
                if hasattr(self, 'warmup_epochs') and epoch < self.warmup_epochs:
                    # Linear warmup
                    warmup_lr = self.config.get('learning_rate', 1e-4) * (epoch + 1) / self.warmup_epochs
                    for param_group in self.optimizer.param_groups:
                        param_group['lr'] = warmup_lr
                    current_lr = warmup_lr
                else:
                    self.scheduler.step()
                    current_lr = self.scheduler.get_last_lr()[0]
            else:
                current_lr = self.scheduler.get_last_lr()[0]
            
            # Guardar en historial
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['val_mae'].append(val_mae)
            self.history['val_rmse'].append(val_rmse)
            self.history['val_r2'].append(val_r2)
            self.history['learning_rate'].append(current_lr)
            
            # Early stopping mejorado: considerar múltiples métricas
            improvement_threshold = self.config.get('improvement_threshold', 1e-4)
            
            # Calcular mejora relativa
            if val_loss < self.best_val_loss * (1 - improvement_threshold):
                improvement = (self.best_val_loss - val_loss) / self.best_val_loss
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.best_model_state = self.model.state_dict().copy()
                logger.info(f"Mejora detectada: {improvement*100:.2f}% (Val Loss: {val_loss:.4f})")
            else:
                self.patience_counter += 1
            
            # Log de época
            epoch_time = time.time() - epoch_start
            logger.info(
                f"Epoch {epoch+1}/{self.config['epochs']} - "
                f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                f"Val MAE: {val_mae:.4f}, Val RMSE: {val_rmse:.4f}, "
                f"Val R²: {val_r2:.4f}, LR: {current_lr:.2e}, "
                f"Time: {epoch_time:.2f}s"
            )
            
            # Early stopping mejorado: solo después de épocas mínimas
            min_epochs = self.config.get('min_epochs', 50)
            if epoch + 1 >= min_epochs and self.patience_counter >= self.early_stopping_patience:
                logger.info(f"Early stopping en época {epoch+1} (después de {min_epochs} épocas mínimas)")
                break
        
        # Cargar mejor modelo
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            logger.info("Mejor modelo cargado")
        
        total_time = time.time() - start_time
        logger.info(f"Entrenamiento completado en {total_time:.2f}s")
        
        return self.history
    
    def _convert_to_native_types(self, obj):
        """
        Convierte valores de NumPy/PyTorch a tipos nativos de Python para serialización JSON.
        
        Args:
            obj: Objeto a convertir (puede ser dict, list, float32, etc.)
            
        Returns:
            Objeto con tipos nativos de Python
        """
        import numpy as np
        import torch
        
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, torch.Tensor):
            return float(obj.item())
        elif isinstance(obj, dict):
            return {key: self._convert_to_native_types(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_native_types(item) for item in obj]
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, int):
            return int(obj)
        else:
            return obj
    
    def save_metrics_to_db(
        self, 
        training_job: TrainingJob = None,
        dataset_info: Dict = None,
        additional_metrics: Dict = None
    ) -> ModelMetrics:
        """
        Guarda las métricas del entrenamiento en la base de datos.
        
        Args:
            training_job: Trabajo de entrenamiento asociado
            dataset_info: Información del dataset usado
            additional_metrics: Métricas adicionales específicas
            
        Returns:
            Instancia de ModelMetrics creada
        """
        try:
            # Obtener métricas finales del historial y convertir a tipos nativos
            final_val_loss = float(self.history['val_loss'][-1]) if self.history['val_loss'] else 0.0
            final_val_mae = float(self.history['val_mae'][-1]) if self.history['val_mae'] else 0.0
            final_val_rmse = float(self.history['val_rmse'][-1]) if self.history['val_rmse'] else 0.0
            final_val_r2 = float(self.history['val_r2'][-1]) if self.history['val_r2'] else 0.0
            
            # Convertir best_val_loss a float nativo
            best_val_loss = float(self.best_val_loss) if self.best_val_loss is not None else None
            
            # Calcular MAPE si es posible y convertir a tipo nativo
            mape = None
            if additional_metrics and 'mape' in additional_metrics:
                mape_value = additional_metrics['mape']
                mape = float(mape_value) if mape_value is not None else None
            
            # Obtener información del dataset
            train_size = dataset_info.get('train_size', 0) if dataset_info else 0
            val_size = dataset_info.get('val_size', 0) if dataset_info else 0
            test_size = dataset_info.get('test_size', 0) if dataset_info else 0
            total_size = train_size + val_size + test_size
            
            # Obtener usuario por defecto (admin) si no se especifica
            try:
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except:
                user = None
            
            # Crear instancia de ModelMetrics
            model_metrics = ModelMetrics.objects.create(
                model_name=f"regression_{self.target}",
                model_type='regression',
                target=self.target,
                version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                training_job=training_job,
                created_by=user,
                metric_type='validation',
                
                # Métricas principales
                mae=final_val_mae,
                mse=final_val_loss,  # MSE es aproximadamente igual a la pérdida de validación
                rmse=final_val_rmse,
                r2_score=final_val_r2,
                mape=mape,
                
                # Métricas adicionales (convertir a tipos nativos)
                additional_metrics=self._convert_to_native_types(additional_metrics) if additional_metrics else {},
                
                # Información del dataset
                dataset_size=int(total_size),
                train_size=int(train_size),
                validation_size=int(val_size),
                test_size=int(test_size),
                
                # Configuración del modelo
                epochs=int(self.config.get('epochs', 50)),
                batch_size=int(self.config.get('batch_size', 32)),
                learning_rate=float(self.config.get('learning_rate', 1e-4)),
                
                # Parámetros específicos del modelo (convertir a tipos nativos)
                model_params=self._convert_to_native_types({
                    'model_type': self.config.get('model_type', 'resnet18'),
                    'pretrained': bool(self.config.get('pretrained', True)),
                    'dropout_rate': float(self.config.get('dropout_rate', 0.2)),
                    'weight_decay': float(self.config.get('weight_decay', 1e-4)),
                    'early_stopping_patience': int(self.config.get('early_stopping_patience', 10)),
                    'best_val_loss': best_val_loss,
                }),
                
                # Información de rendimiento
                training_time_seconds=None,  # Se puede calcular después
                inference_time_ms=None,  # Se puede medir después
                
                # Notas
                notes=f"Modelo entrenado para {self.target} usando {get_model_info(self.model)}",
                is_best_model=False,  # Se puede marcar después si es el mejor
                is_production_model=False
            )
            
            logger.info(f"[OK] Métricas guardadas en DB para {self.target}: MAE={final_val_mae:.4f}, RMSE={final_val_rmse:.4f}, R²={final_val_r2:.4f}")
            return model_metrics
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando métricas en DB para {self.target}: {e}")
            raise
    
    def save_model(self, file_path: Path) -> None:
        """Guarda el modelo entrenado."""
        try:
            ensure_dir_exists(file_path.parent)
            
            # Información del modelo
            model_info = {
                'target': self.target,
                'model_type': type(self.model).__name__,
                'config': self.config,
                'best_val_loss': self.best_val_loss,
                'training_history': self.history,
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar modelo y metadatos
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_info': model_info,
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict()
            }, file_path)
            
            # Verificar que el archivo se guardó correctamente
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[OK] Modelo guardado exitosamente en {file_path} ({file_path.stat().st_size} bytes)")
            else:
                logger.error(f"[ERROR] Error: El archivo no se guardó correctamente: {file_path}")
                raise IOError(f"No se pudo guardar el modelo en {file_path}")
                
        except Exception as e:
            logger.error(f"[ERROR] Error guardando modelo para {self.target}: {e}")
            raise


def train_single_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    target: str,
    config: Dict,
    device: torch.device,
    training_job: TrainingJob = None,
    dataset_info: Dict = None,
    save_metrics: bool = True
) -> Dict[str, List[float]]:
    """
    Entrena un modelo individual.
    
    Args:
        model: Modelo a entrenar
        train_loader: DataLoader de entrenamiento
        val_loader: DataLoader de validación
        scalers: Escaladores para normalización
        target: Target a entrenar
        config: Configuración de entrenamiento
        device: Dispositivo para entrenamiento
        training_job: Trabajo de entrenamiento asociado
        dataset_info: Información del dataset usado
        save_metrics: Si guardar métricas en la base de datos
        
    Returns:
        Historial de entrenamiento
    """
    trainer = RegressionTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        scalers=scalers,
        target=target,
        device=device,
        config=config
    )
    
    history = trainer.train()
    
    # Guardar modelo
    artifacts_dir = get_regressors_artifacts_dir()
    model_path = artifacts_dir / f"{target}.pt"
    trainer.save_model(model_path)
    
    # Guardar métricas en la base de datos
    if save_metrics:
        try:
            # Calcular métricas adicionales si es necesario
            additional_metrics = {}
            
            # Calcular MAPE si es posible
            if history['val_loss'] and history['val_mae']:
                # MAPE aproximado basado en MAE y valores promedio
                try:
                    # Convertir todos los valores a tipos nativos de Python
                    additional_metrics['final_train_loss'] = float(history['train_loss'][-1]) if history['train_loss'] else 0.0
                    additional_metrics['final_val_loss'] = float(history['val_loss'][-1])
                    additional_metrics['final_val_mae'] = float(history['val_mae'][-1])
                    additional_metrics['final_val_rmse'] = float(history['val_rmse'][-1])
                    additional_metrics['final_val_r2'] = float(history['val_r2'][-1])
                    additional_metrics['epochs_completed'] = int(len(history['train_loss']))
                    additional_metrics['early_stopping_triggered'] = bool(len(history['train_loss']) < config.get('epochs', 50))
                except Exception as e:
                    logger.warning(f"No se pudieron calcular métricas adicionales: {e}")
            
            # Guardar métricas en la base de datos
            model_metrics = trainer.save_metrics_to_db(
                training_job=training_job,
                dataset_info=dataset_info,
                additional_metrics=additional_metrics
            )
            
            logger.info(f"[OK] Métricas del modelo {target} guardadas con ID: {model_metrics.id}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando métricas para {target}: {e}")
            # No interrumpir el entrenamiento si falla el guardado de métricas
    
    return history


def train_multi_head_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    scalers: CacaoScalers,
    config: Dict,
    device: torch.device,
    training_job: TrainingJob = None,
    dataset_info: Dict = None,
    save_metrics: bool = True
) -> Dict[str, List[float]]:
    """
    Entrena un modelo multi-head.
    
    Args:
        model: Modelo multi-head a entrenar
        train_loader: DataLoader de entrenamiento
        val_loader: DataLoader de validación
        scalers: Escaladores para normalización
        config: Configuración de entrenamiento
        device: Dispositivo para entrenamiento
        training_job: Trabajo de entrenamiento asociado
        dataset_info: Información del dataset usado
        save_metrics: Si guardar métricas en la base de datos
        
    Returns:
        Historial de entrenamiento
    """
    logger.info("Entrenando modelo multi-head")
    
    # Configurar optimizador
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.get('learning_rate', 1e-4),
        weight_decay=config.get('weight_decay', 1e-4)
    )
    
    # Configurar scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config.get('epochs', 50),
        eta_min=config.get('min_lr', 1e-6)
    )
    
    criterion = nn.MSELoss()
    
    # Historial
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_mae': {target: [] for target in TARGETS},
        'val_rmse': {target: [] for target in TARGETS},
        'val_r2': {target: [] for target in TARGETS},
        'learning_rate': []
    }
    
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None
    
    model = model.to(device)
    
    for epoch in range(config['epochs']):
        # Entrenamiento
        model.train()
        train_loss = 0.0
        
        for batch_idx, (images, targets_dict) in enumerate(train_loader):
            images = images.to(device)
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = 0.0
            
            # Calcular pérdida para cada target
            for target in TARGETS:
                target_values = targets_dict[target].to(device)
                target_loss = criterion(outputs[target], target_values)
                loss += target_loss
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validación
        model.eval()
        val_loss = 0.0
        val_metrics = {target: {'mae': [], 'rmse': [], 'r2': []} for target in TARGETS}
        
        with torch.no_grad():
            for images, targets_dict in val_loader:
                images = images.to(device)
                outputs = model(images)
                
                batch_loss = 0.0
                
                for target in TARGETS:
                    target_values = targets_dict[target].to(device)
                    target_loss = criterion(outputs[target], target_values)
                    batch_loss += target_loss
                    
                    # Calcular métricas
                    pred = outputs[target].cpu().numpy().flatten()
                    true = target_values.cpu().numpy().flatten()
                    
                    mae = np.mean(np.abs(pred - true))
                    rmse = np.sqrt(np.mean((pred - true) ** 2))
                    
                    ss_res = np.sum((true - pred) ** 2)
                    ss_tot = np.sum((true - np.mean(true)) ** 2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                    
                    val_metrics[target]['mae'].append(mae)
                    val_metrics[target]['rmse'].append(rmse)
                    val_metrics[target]['r2'].append(r2)
                
                val_loss += batch_loss
        
        # Promediar métricas
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        
        # Guardar en historial
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['learning_rate'].append(scheduler.get_last_lr()[0])
        
        for target in TARGETS:
            history['val_mae'][target].append(np.mean(val_metrics[target]['mae']))
            history['val_rmse'][target].append(np.mean(val_metrics[target]['rmse']))
            history['val_r2'][target].append(np.mean(val_metrics[target]['r2']))
        
        # Early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            best_model_state = model.state_dict().copy()
        else:
            patience_counter += 1
        
        scheduler.step()
        
        # Log
        logger.info(
            f"Epoch {epoch+1}/{config['epochs']} - "
            f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
        )
        
        for target in TARGETS:
            logger.info(
                f"  {target}: MAE={history['val_mae'][target][-1]:.4f}, "
                f"RMSE={history['val_rmse'][target][-1]:.4f}, "
                f"R²={history['val_r2'][target][-1]:.4f}"
            )
        
        if patience_counter >= config.get('early_stopping_patience', 10):
            logger.info(f"Early stopping en época {epoch+1}")
            break
    
    # Guardar mejor modelo
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    # Guardar modelo multi-head
    artifacts_dir = get_regressors_artifacts_dir()
    model_path = artifacts_dir / "multihead.pt"
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_info': {
            'model_type': 'MultiHeadRegression',
            'config': config,
            'best_val_loss': best_val_loss,
            'training_history': history,
            'timestamp': datetime.now().isoformat()
        }
    }, model_path)
    
    logger.info(f"Modelo multi-head guardado en {model_path}")
    
    # Guardar métricas en la base de datos para cada target
    if save_metrics:
        try:
            # Obtener usuario por defecto
            try:
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except:
                user = None
            
            # Obtener información del dataset
            train_size = dataset_info.get('train_size', 0) if dataset_info else 0
            val_size = dataset_info.get('val_size', 0) if dataset_info else 0
            test_size = dataset_info.get('test_size', 0) if dataset_info else 0
            total_size = train_size + val_size + test_size
            
            # Guardar métricas para cada target
            for target in TARGETS:
                if target in history['val_mae'] and history['val_mae'][target]:
                    # Convertir métricas a tipos nativos
                    final_val_mae = float(history['val_mae'][target][-1])
                    final_val_rmse = float(history['val_rmse'][target][-1])
                    final_val_r2 = float(history['val_r2'][target][-1])
                    final_val_loss = float(history['val_loss'][-1]) if history['val_loss'] else 0.0
                    final_train_loss = float(history['train_loss'][-1]) if history['train_loss'] else 0.0
                    best_val_loss_native = float(best_val_loss) if best_val_loss is not None else None
                    
                    # Métricas adicionales específicas del multi-head (convertir a tipos nativos)
                    additional_metrics = {
                        'model_type': 'multi_head',
                        'final_train_loss': final_train_loss,
                        'final_val_loss': final_val_loss,
                        'epochs_completed': int(len(history['train_loss'])),
                        'early_stopping_triggered': bool(len(history['train_loss']) < config.get('epochs', 50)),
                        'best_val_loss': best_val_loss_native,
                    }
                    
                    # Crear métricas para este target
                    model_metrics = ModelMetrics.objects.create(
                        model_name=f"multihead_regression",
                        model_type='regression',
                        target=target,
                        version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        training_job=training_job,
                        created_by=user,
                        metric_type='validation',
                        
                        # Métricas principales
                        mae=final_val_mae,
                        mse=final_val_loss,
                        rmse=final_val_rmse,
                        r2_score=final_val_r2,
                        mape=None,
                        
                        # Métricas adicionales (ya convertidas)
                        additional_metrics=additional_metrics,
                        
                        # Información del dataset
                        dataset_size=int(total_size),
                        train_size=int(train_size),
                        validation_size=int(val_size),
                        test_size=int(test_size),
                        
                        # Configuración del modelo
                        epochs=int(config.get('epochs', 50)),
                        batch_size=int(config.get('batch_size', 32)),
                        learning_rate=float(config.get('learning_rate', 1e-4)),
                        
                        # Parámetros específicos del modelo (convertir a tipos nativos)
                        model_params={
                            'model_type': str(config.get('model_type', 'resnet18')),
                            'pretrained': bool(config.get('pretrained', True)),
                            'dropout_rate': float(config.get('dropout_rate', 0.2)),
                            'weight_decay': float(config.get('weight_decay', 1e-4)),
                            'early_stopping_patience': int(config.get('early_stopping_patience', 10)),
                            'best_val_loss': best_val_loss_native,
                        },
                        
                        # Información de rendimiento
                        training_time_seconds=None,
                        inference_time_ms=None,
                        
                        # Notas
                        notes=f"Modelo multi-head entrenado para {target}",
                        is_best_model=False,
                        is_production_model=False
                    )
                    
                    logger.info(f"[OK] Métricas del modelo multi-head para {target} guardadas con ID: {model_metrics.id}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando métricas del modelo multi-head: {e}")
            # No interrumpir el entrenamiento si falla el guardado de métricas
    
    return history


def get_device() -> torch.device:
    """Obtiene el dispositivo disponible para entrenamiento."""
    if torch.cuda.is_available():
        device = torch.device('cuda')
        logger.info(f"Usando GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        logger.info("Usando CPU")
    
    return device


def create_training_job(
    job_type: str = 'regression',
    model_name: str = 'regression_model',
    dataset_size: int = 0,
    config: Dict = None,
    user: User = None
) -> TrainingJob:
    """
    Crea un TrainingJob para asociar con las métricas.
    
    Args:
        job_type: Tipo de trabajo de entrenamiento
        model_name: Nombre del modelo
        dataset_size: Tamaño del dataset
        config: Configuración del entrenamiento
        user: Usuario que ejecuta el entrenamiento
        
    Returns:
        Instancia de TrainingJob creada
    """
    try:
        # Obtener usuario por defecto si no se especifica
        if not user:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        
        # Crear job ID único con microsegundos para evitar duplicados
        import time
        job_id = f"{job_type}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000000) % 1000000}"
        
        # Crear TrainingJob
        training_job = TrainingJob.objects.create(
            job_id=job_id,
            job_type=job_type,
            model_name=model_name,
            dataset_size=dataset_size,
            epochs=config.get('epochs', 50) if config else 50,
            batch_size=config.get('batch_size', 32) if config else 32,
            learning_rate=config.get('learning_rate', 1e-4) if config else 1e-4,
            config_params=config or {},
            created_by=user,
            status='running'
        )
        
        logger.info(f"[OK] TrainingJob creado con ID: {job_id}")
        return training_job
        
    except Exception as e:
        logger.error(f"[ERROR] Error creando TrainingJob: {e}")
        return None


def update_training_job_metrics(
    training_job: TrainingJob,
    metrics: Dict,
    model_path: str = None
) -> None:
    """
    Actualiza un TrainingJob con las métricas finales.
    
    Args:
        training_job: TrainingJob a actualizar
        metrics: Métricas del entrenamiento
        model_path: Ruta del modelo entrenado
    """
    try:
        if training_job:
            training_job.mark_completed(
                metrics=metrics,
                model_path=model_path
            )
            logger.info(f"[OK] TrainingJob {training_job.job_id} actualizado con métricas")
    except Exception as e:
        logger.error(f"[ERROR] Error actualizando TrainingJob: {e}")
