<template>
  <div class="configuracion-container">
    <div class="configuracion-header">
      <h1>Configuración del Sistema</h1>
      <p>Gestiona la configuración general de la aplicación</p>
    </div>
    
    <div class="configuracion-content">
      <div class="config-section">
        <h2>Configuración General</h2>
        <div class="config-form">
          <div class="form-group">
            <label for="appName">Nombre de la Aplicación</label>
            <input type="text" id="appName" v-model="config.appName" placeholder="CacaoScan">
          </div>
          
          <div class="form-group">
            <label for="maxFileSize">Tamaño Máximo de Archivo (MB)</label>
            <input type="number" id="maxFileSize" v-model="config.maxFileSize" min="1" max="100">
          </div>
          
          <div class="form-group">
            <label for="sessionTimeout">Tiempo de Sesión (minutos)</label>
            <input type="number" id="sessionTimeout" v-model="config.sessionTimeout" min="15" max="480">
          </div>
        </div>
      </div>
      
      <div class="config-section">
        <h2>Configuración de Notificaciones</h2>
        <div class="config-form">
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="config.emailNotifications">
              <span>Habilitar notificaciones por email</span>
            </label>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="config.pushNotifications">
              <span>Habilitar notificaciones push</span>
            </label>
          </div>
        </div>
      </div>
      
      <div class="config-actions">
        <button class="btn btn-primary" @click="saveConfig">Guardar Cambios</button>
        <button class="btn btn-secondary" @click="resetConfig">Restablecer</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Configuracion',
  data() {
    return {
      config: {
        appName: 'CacaoScan',
        maxFileSize: 10,
        sessionTimeout: 120,
        emailNotifications: true,
        pushNotifications: false
      }
    };
  },
  methods: {
    saveConfig() {
      // Aquí se implementaría la lógica para guardar la configuración
      console.log('Configuración guardada:', this.config);
      // Mostrar mensaje de éxito
      alert('Configuración guardada exitosamente');
    },
    resetConfig() {
      // Restablecer a valores por defecto
      this.config = {
        appName: 'CacaoScan',
        maxFileSize: 10,
        sessionTimeout: 120,
        emailNotifications: true,
        pushNotifications: false
      };
    }
  }
};
</script>

<style scoped>
.configuracion-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.configuracion-header {
  margin-bottom: 2rem;
  text-align: center;
}

.configuracion-header h1 {
  color: #059669;
  margin-bottom: 0.5rem;
}

.configuracion-header p {
  color: #6b7280;
  font-size: 1.1rem;
}

.configuracion-content {
  display: grid;
  gap: 2rem;
}

.config-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.config-section h2 {
  color: #374151;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.config-form {
  display: grid;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #374151;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  accent-color: #059669;
}

.config-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #059669;
  color: white;
}

.btn-primary:hover {
  background: #047857;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .configuracion-container {
    padding: 1rem;
  }
  
  .config-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
