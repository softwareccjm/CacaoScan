"""
Script de entrenamiento para modelos de regresiÃ³n de dimensiones de cacao.
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
    """Entrenador para modelos de regresiÃ³n de cacao."""
    
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
            val_loader: DataLoader de validaciÃ³n
            scalers: Escaladores para normalizaciÃ³n
            target: Target a entrenar
            device: Dispositivo para entrenamiento
            config: ConfiguraciÃ³n de entrenamiento
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.scalers = scalers
        self.target = target
        self.device = device
        self.config = config
        
        # Configurar optimizador
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config.get('learning_rate', 1e-4),
            weight_decay=config.get('weight_decay', 1e-4)
        )
        
        # Configurar scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=config.get('epochs', 50),
            eta_min=config.get('min_lr', 1e-6)
        )
        
        # Criterio de pÃ©rdida
        self.criterion = nn.MSELoss()
        
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
        """Entrena el modelo por una Ã©poca."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, (images, targets) in enumerate(self.train_loader):
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            
            # Calcular pÃ©rdida
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # Log periÃ³dico
            if batch_idx % 10 == 0:
                logger.debug(f"Epoch batch {batch_idx}/{len(self.train_loader)}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate_epoch(self) -> Tuple[float, float, float, float]:
        """
        Valida el modelo por una Ã©poca.
        
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
                
                # Convertir a numpy para mÃ©tricas
                predictions = outputs.cpu().numpy().flatten()
                targets_np = targets.cpu().numpy().flatten()
                
                all_predictions.extend(predictions)
                all_targets.extend(targets_np)
        
        # Calcular mÃ©tricas
        all_predictions = np.array(all_predictions)
        all_targets = np.array(all_targets)
        
        avg_loss = total_loss / len(self.val_loader)
        mae = np.mean(np.abs(all_predictions - all_targets))
        rmse = np.sqrt(np.mean((all_predictions - all_targets) ** 2))
        
        # RÂ² score
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
        logger.info(f"Ã‰pocas: {self.config['epochs']}, Batch size: {self.config['batch_size']}")
        
        start_time = time.time()
        
        for epoch in range(self.config['epochs']):
            epoch_start = time.time()
            
            # Entrenar
            train_loss = self.train_epoch()
            
            # Validar
            val_loss, val_mae, val_rmse, val_r2 = self.validate_epoch()
            
            # Actualizar scheduler
            self.scheduler.step()
            current_lr = self.scheduler.get_last_lr()[0]
            
            # Guardar en historial
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['val_mae'].append(val_mae)
            self.history['val_rmse'].append(val_rmse)
            self.history['val_r2'].append(val_r2)
            self.history['learning_rate'].append(current_lr)
            
            # Early stopping check
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.best_model_state = self.model.state_dict().copy()
            else:
                self.patience_counter += 1
            
            # Log de Ã©poca
            epoch_time = time.time() - epoch_start
            logger.info(
                f"Epoch {epoch+1}/{self.config['epochs']} - "
                f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                f"Val MAE: {val_mae:.4f}, Val RMSE: {val_rmse:.4f}, "
                f"Val RÂ²: {val_r2:.4f}, LR: {current_lr:.2e}, "
                f"Time: {epoch_time:.2f}s"
            )
            
            # Early stopping
            if self.patience_counter >= self.early_stopping_patience:
                logger.info(f"Early stopping en Ã©poca {epoch+1}")
                break
        
        # Cargar mejor modelo
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            logger.info("Mejor modelo cargado")
        
        total_time = time.time() - start_time
        logger.info(f"Entrenamiento completado en {total_time:.2f}s")
        
        return self.history
    
    def save_metrics_to_db(
        self, 
        training_job: TrainingJob = None,
        dataset_info: Dict = None,
        additional_metrics: Dict = None
    ) -> ModelMetrics:
        """
        Guarda las mÃ©tricas del entrenamiento en la base de datos.
        
        Args:
            training_job: Trabajo de entrenamiento asociado
            dataset_info: InformaciÃ³n del dataset usado
            additional_metrics: MÃ©tricas adicionales especÃ­ficas
            
        Returns:
            Instancia de ModelMetrics creada
        """
        try:
            # Obtener mÃ©tricas finales del historial
            final_val_loss = self.history['val_loss'][-1] if self.history['val_loss'] else 0.0
            final_val_mae = self.history['val_mae'][-1] if self.history['val_mae'] else 0.0
            final_val_rmse = self.history['val_rmse'][-1] if self.history['val_rmse'] else 0.0
            final_val_r2 = self.history['val_r2'][-1] if self.history['val_r2'] else 0.0
            
            # Calcular MAPE si es posible
            mape = None
            if additional_metrics and 'mape' in additional_metrics:
                mape = additional_metrics['mape']
            
            # Obtener informaciÃ³n del dataset
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
                
                # MÃ©tricas principales
                mae=final_val_mae,
                mse=final_val_loss,  # MSE es aproximadamente igual a la pÃ©rdida de validaciÃ³n
                rmse=final_val_rmse,
                r2_score=final_val_r2,
                mape=mape,
                
                # MÃ©tricas adicionales
                additional_metrics=additional_metrics or {},
                
                # InformaciÃ³n del dataset
                dataset_size=total_size,
                train_size=train_size,
                validation_size=val_size,
                test_size=test_size,
                
                # ConfiguraciÃ³n del modelo
                epochs=self.config.get('epochs', 50),
                batch_size=self.config.get('batch_size', 32),
                learning_rate=self.config.get('learning_rate', 1e-4),
                
                # ParÃ¡metros especÃ­ficos del modelo
                model_params={
                    'model_type': self.config.get('model_type', 'resnet18'),
                    'pretrained': self.config.get('pretrained', True),
                    'dropout_rate': self.config.get('dropout_rate', 0.2),
                    'weight_decay': self.config.get('weight_decay', 1e-4),
                    'early_stopping_patience': self.config.get('early_stopping_patience', 10),
                    'best_val_loss': self.best_val_loss,
                },
                
                # InformaciÃ³n de rendimiento
                training_time_seconds=None,  # Se puede calcular despuÃ©s
                inference_time_ms=None,  # Se puede medir despuÃ©s
                
                # Notas
                notes=f"Modelo entrenado para {self.target} usando {get_model_info(self.model)}",
                is_best_model=False,  # Se puede marcar despuÃ©s si es el mejor
                is_production_model=False
            )
            
            logger.info(f"âœ… MÃ©tricas guardadas en DB para {self.target}: MAE={final_val_mae:.4f}, RMSE={final_val_rmse:.4f}, RÂ²={final_val_r2:.4f}")
            return model_metrics
            
        except Exception as e:
            logger.error(f"âŒ Error guardando mÃ©tricas en DB para {self.target}: {e}")
            raise
    
    def save_model(self, file_path: Path) -> None:
        """Guarda el modelo entrenado."""
        try:
            ensure_dir_exists(file_path.parent)
            
            # InformaciÃ³n del modelo
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
            
            # Verificar que el archivo se guardÃ³ correctamente
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"âœ… Modelo guardado exitosamente en {file_path} ({file_path.stat().st_size} bytes)")
            else:
                logger.error(f"âŒ Error: El archivo no se guardÃ³ correctamente: {file_path}")
                raise IOError(f"No se pudo guardar el modelo en {file_path}")
                
        except Exception as e:
            logger.error(f"âŒ Error guardando modelo para {self.target}: {e}")
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
        val_loader: DataLoader de validaciÃ³n
        scalers: Escaladores para normalizaciÃ³n
        target: Target a entrenar
        config: ConfiguraciÃ³n de entrenamiento
        device: Dispositivo para entrenamiento
        training_job: Trabajo de entrenamiento asociado
        dataset_info: InformaciÃ³n del dataset usado
        save_metrics: Si guardar mÃ©tricas en la base de datos
        
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
    
    # Guardar mÃ©tricas en la base de datos
    if save_metrics:
        try:
            # Calcular mÃ©tricas adicionales si es necesario
            additional_metrics = {}
            
            # Calcular MAPE si es posible
            if history['val_loss'] and history['val_mae']:
                # MAPE aproximado basado en MAE y valores promedio
                try:
                    # Esto es una aproximaciÃ³n, el MAPE real requiere los valores reales
                    additional_metrics['final_train_loss'] = history['train_loss'][-1] if history['train_loss'] else 0.0
                    additional_metrics['final_val_loss'] = history['val_loss'][-1]
                    additional_metrics['final_val_mae'] = history['val_mae'][-1]
                    additional_metrics['final_val_rmse'] = history['val_rmse'][-1]
                    additional_metrics['final_val_r2'] = history['val_r2'][-1]
                    additional_metrics['epochs_completed'] = len(history['train_loss'])
                    additional_metrics['early_stopping_triggered'] = len(history['train_loss']) < config.get('epochs', 50)
                except Exception as e:
                    logger.warning(f"No se pudieron calcular mÃ©tricas adicionales: {e}")
            
            # Guardar mÃ©tricas en la base de datos
            model_metrics = trainer.save_metrics_to_db(
                training_job=training_job,
                dataset_info=dataset_info,
                additional_metrics=additional_metrics
            )
            
            logger.info(f"âœ… MÃ©tricas del modelo {target} guardadas con ID: {model_metrics.id}")
            
        except Exception as e:
            logger.error(f"âŒ Error guardando mÃ©tricas para {target}: {e}")
            # No interrumpir el entrenamiento si falla el guardado de mÃ©tricas
    
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
        val_loader: DataLoader de validaciÃ³n
        scalers: Escaladores para normalizaciÃ³n
        config: ConfiguraciÃ³n de entrenamiento
        device: Dispositivo para entrenamiento
        training_job: Trabajo de entrenamiento asociado
        dataset_info: InformaciÃ³n del dataset usado
        save_metrics: Si guardar mÃ©tricas en la base de datos
        
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
            
            # Calcular pÃ©rdida para cada target
            for target in TARGETS:
                target_values = targets_dict[target].to(device)
                target_loss = criterion(outputs[target], target_values)
                loss += target_loss
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # ValidaciÃ³n
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
                    
                    # Calcular mÃ©tricas
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
        
        # Promediar mÃ©tricas
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
                f"RÂ²={history['val_r2'][target][-1]:.4f}"
            )
        
        if patience_counter >= config.get('early_stopping_patience', 10):
            logger.info(f"Early stopping en Ã©poca {epoch+1}")
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
    
    # Guardar mÃ©tricas en la base de datos para cada target
    if save_metrics:
        try:
            # Obtener usuario por defecto
            try:
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except:
                user = None
            
            # Obtener informaciÃ³n del dataset
            train_size = dataset_info.get('train_size', 0) if dataset_info else 0
            val_size = dataset_info.get('val_size', 0) if dataset_info else 0
            test_size = dataset_info.get('test_size', 0) if dataset_info else 0
            total_size = train_size + val_size + test_size
            
            # Guardar mÃ©tricas para cada target
            for target in TARGETS:
                if target in history['val_mae'] and history['val_mae'][target]:
                    final_val_mae = history['val_mae'][target][-1]
                    final_val_rmse = history['val_rmse'][target][-1]
                    final_val_r2 = history['val_r2'][target][-1]
                    
                    # MÃ©tricas adicionales especÃ­ficas del multi-head
                    additional_metrics = {
                        'model_type': 'multi_head',
                        'final_train_loss': history['train_loss'][-1] if history['train_loss'] else 0.0,
                        'final_val_loss': history['val_loss'][-1] if history['val_loss'] else 0.0,
                        'epochs_completed': len(history['train_loss']),
                        'early_stopping_triggered': len(history['train_loss']) < config.get('epochs', 50),
                        'best_val_loss': best_val_loss,
                    }
                    
                    # Crear mÃ©tricas para este target
                    model_metrics = ModelMetrics.objects.create(
                        model_name=f"multihead_regression",
                        model_type='regression',
                        target=target,
                        version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        training_job=training_job,
                        created_by=user,
                        metric_type='validation',
                        
                        # MÃ©tricas principales
                        mae=final_val_mae,
                        mse=history['val_loss'][-1] if history['val_loss'] else 0.0,
                        rmse=final_val_rmse,
                        r2_score=final_val_r2,
                        mape=None,
                        
                        # MÃ©tricas adicionales
                        additional_metrics=additional_metrics,
                        
                        # InformaciÃ³n del dataset
                        dataset_size=total_size,
                        train_size=train_size,
                        validation_size=val_size,
                        test_size=test_size,
                        
                        # ConfiguraciÃ³n del modelo
                        epochs=config.get('epochs', 50),
                        batch_size=config.get('batch_size', 32),
                        learning_rate=config.get('learning_rate', 1e-4),
                        
                        # ParÃ¡metros especÃ­ficos del modelo
                        model_params={
                            'model_type': config.get('model_type', 'resnet18'),
                            'pretrained': config.get('pretrained', True),
                            'dropout_rate': config.get('dropout_rate', 0.2),
                            'weight_decay': config.get('weight_decay', 1e-4),
                            'early_stopping_patience': config.get('early_stopping_patience', 10),
                            'best_val_loss': best_val_loss,
                        },
                        
                        # InformaciÃ³n de rendimiento
                        training_time_seconds=None,
                        inference_time_ms=None,
                        
                        # Notas
                        notes=f"Modelo multi-head entrenado para {target}",
                        is_best_model=False,
                        is_production_model=False
                    )
                    
                    logger.info(f"âœ… MÃ©tricas del modelo multi-head para {target} guardadas con ID: {model_metrics.id}")
            
        except Exception as e:
            logger.error(f"âŒ Error guardando mÃ©tricas del modelo multi-head: {e}")
            # No interrumpir el entrenamiento si falla el guardado de mÃ©tricas
    
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
    Crea un TrainingJob para asociar con las mÃ©tricas.
    
    Args:
        job_type: Tipo de trabajo de entrenamiento
        model_name: Nombre del modelo
        dataset_size: TamaÃ±o del dataset
        config: ConfiguraciÃ³n del entrenamiento
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
        
        # Crear job ID Ãºnico con microsegundos para evitar duplicados
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
        
        logger.info(f"âœ… TrainingJob creado con ID: {job_id}")
        return training_job
        
    except Exception as e:
        logger.error(f"âŒ Error creando TrainingJob: {e}")
        return None


def update_training_job_metrics(
    training_job: TrainingJob,
    metrics: Dict,
    model_path: str = None
) -> None:
    """
    Actualiza un TrainingJob con las mÃ©tricas finales.
    
    Args:
        training_job: TrainingJob a actualizar
        metrics: MÃ©tricas del entrenamiento
        model_path: Ruta del modelo entrenado
    """
    try:
        if training_job:
            training_job.mark_completed(
                metrics=metrics,
                model_path=model_path
            )
            logger.info(f"âœ… TrainingJob {training_job.job_id} actualizado con mÃ©tricas")
    except Exception as e:
        logger.error(f"âŒ Error actualizando TrainingJob: {e}")


