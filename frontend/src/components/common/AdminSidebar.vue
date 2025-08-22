<template>
  <aside class="dashboard-sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Header del sidebar -->
    <div class="sidebar-header">
      <div class="admin-info" @click="toggleSidebar" style="cursor: pointer;" :title="sidebarCollapsed ? 'Expandir menú' : 'Colapsar menú'">
        <div class="admin-avatar">
          <span class="admin-initials">{{ userInitials }}</span>
        </div>
        <div class="admin-details" v-if="!sidebarCollapsed">
          <h3>{{ userName }}</h3>
          <span class="admin-role">{{ userRole }}</span>
        </div>
      </div>
    </div>

    <!-- Navegación -->
    <nav class="sidebar-nav">
      <ul class="nav-menu">
        <li class="nav-item" :class="{ 'active': activeSection === 'dashboard' }">
          <router-link to="/admin" class="nav-link" :title="sidebarCollapsed ? 'Dashboard' : ''">
            <i class="fas fa-chart-pie"></i>
            <span v-if="!sidebarCollapsed">Dashboard</span>
          </router-link>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'agricultores' }">
          <router-link to="/admin/agricultores" class="nav-link" :title="sidebarCollapsed ? 'Agricultores' : ''">
            <i class="fas fa-users"></i>
            <span v-if="!sidebarCollapsed">Agricultores</span>
          </router-link>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'analisis' }">
          <router-link to="/admin/analisis" class="nav-link" :title="sidebarCollapsed ? 'Análisis' : ''">
            <i class="fas fa-microscope"></i>
            <span v-if="!sidebarCollapsed">Análisis</span>
          </router-link>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'reportes' }">
          <router-link to="/admin/reportes" class="nav-link" :title="sidebarCollapsed ? 'Reportes' : ''">
            <i class="fas fa-file-alt"></i>
            <span v-if="!sidebarCollapsed">Reportes</span>
          </router-link>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'configuracion' }">
          <router-link to="/admin/configuracion" class="nav-link" :title="sidebarCollapsed ? 'Configuración' : ''">
            <i class="fas fa-cog"></i>
            <span v-if="!sidebarCollapsed">Configuración</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Footer del sidebar -->
    <div class="sidebar-footer" v-if="!sidebarCollapsed">
      <div class="quick-stats">
        <div class="stat-item">
          <span class="stat-label">Total Usuarios</span>
          <span class="stat-value">{{ stats.totalUsers }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Análisis Hoy</span>
          <span class="stat-value">{{ stats.todayAnalyses }}</span>
        </div>
      </div>
      
      <!-- Logout Section -->
      <div class="logout-section">
        <button class="logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </div>
    
    <!-- Logout button for collapsed sidebar -->
    <div class="sidebar-footer-collapsed" v-if="sidebarCollapsed">
      <button class="logout-btn-collapsed" @click="logout" title="Cerrar Sesión">
        <i class="fas fa-sign-out-alt"></i>
      </button>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AdminSidebar',
  props: {
    userInitials: {
      type: String,
      default: 'AD'
    },
    userName: {
      type: String,
      default: 'Admin'
    },
    userRole: {
      type: String,
      default: 'Administrador'
    },
    sidebarCollapsed: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      activeSection: '',
      stats: {
        totalUsers: 156,
        todayAnalyses: 24
      }
    };
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar');
    },
    logout() {
      if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        // Limpiar datos de sesión
        localStorage.removeItem('userToken');
        localStorage.removeItem('userRole');
        localStorage.removeItem('sidebarCollapsed');
        localStorage.removeItem('userData');
        localStorage.removeItem('authToken');
        
        // Redirigir al login
        this.$router.push('/login');
      }
    }
  },
  mounted() {
    console.log('AdminSidebar montado, ruta actual:', this.$route.path);
    // Detectar la sección activa al montar el componente
    this.updateActiveSection(this.$route.path);
  },
  watch: {
    $route: {
      handler(to) {
        console.log('Ruta cambiada a:', to.path);
        // Actualizar la sección activa basada en la ruta
        this.updateActiveSection(to.path);
      },
      immediate: true
    }
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar');
    },
    logout() {
      if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        // Limpiar datos de sesión
        localStorage.removeItem('userToken');
        localStorage.removeItem('userRole');
        localStorage.removeItem('sidebarCollapsed');
        localStorage.removeItem('userData');
        localStorage.removeItem('authToken');
        
        // Redirigir al login
        this.$router.push('/login');
      }
    },
    updateActiveSection(path) {
      console.log('updateActiveSection llamado con path:', path);
      
      // Actualizar la sección activa basada en la ruta
      if (path.includes('/admin/agricultores')) {
        this.activeSection = 'agricultores';
        console.log('Sección establecida como: agricultores');
      } else if (path.includes('/admin/analisis')) {
        this.activeSection = 'analisis';
        console.log('Sección establecida como: analisis');
      } else if (path.includes('/admin/reportes')) {
        this.activeSection = 'reportes';
        console.log('Sección establecida como: reportes');
      } else if (path.includes('/admin/configuracion')) {
        this.activeSection = 'configuracion';
        console.log('Sección establecida como: configuracion');
      } else if (path === '/admin') {
        this.activeSection = 'dashboard';
        console.log('Sección establecida como: dashboard');
      } else {
        console.log('No se encontró coincidencia para la ruta:', path);
      }
      
      console.log('Estado final - Ruta actual:', path, 'Sección activa:', this.activeSection);
      
      // Debug adicional
      this.$nextTick(() => {
        console.log('Después de $nextTick - activeSection:', this.activeSection);
        const activeElements = document.querySelectorAll('.nav-item.active');
        console.log('Elementos con clase active encontrados:', activeElements.length);
        activeElements.forEach((el, index) => {
          console.log(`Elemento activo ${index}:`, el);
        });
      });
    }
  }
};
</script>

<style scoped>
/* Estilos del sidebar del admin basados en el del agricultor */
.dashboard-sidebar {
  width: 280px;
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
  transition: all 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-collapsed {
  width: 70px;
}

.sidebar-collapsed .sidebar-header {
  padding: 1rem 0.5rem;
  justify-content: center;
}

.sidebar-collapsed .admin-info {
  justify-content: center;
  padding: 0.5rem;
}

.sidebar-collapsed .admin-info:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.sidebar-collapsed .admin-avatar {
  animation: subtle-pulse 2s infinite;
}

@keyframes subtle-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 255, 255, 0.1);
  }
}

.sidebar-collapsed .admin-avatar {
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
}

.sidebar-collapsed .nav-link {
  padding: 1rem;
  justify-content: center;
  margin-right: 0;
}

.sidebar-collapsed .nav-link i {
  margin: 0;
}

.sidebar-collapsed .nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: none;
}

.sidebar-collapsed .nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin: 0.5rem;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
  border-radius: 8px;
  padding: 0.5rem;
}

.admin-info:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.admin-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  transition: all 0.2s ease;
  position: relative;
}

.admin-initials {
  color: #059669;
  font-weight: bold;
}

.admin-info:active {
  transform: scale(0.95);
}

/* Indicador de estado del sidebar */
.sidebar-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px 0 0 2px;
  transition: all 0.3s ease;
}

.sidebar-collapsed .sidebar-header::before {
  background: rgba(255, 255, 255, 0.6);
  width: 6px;
}

.admin-details h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.admin-role {
  font-size: 0.9rem;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0.25rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  margin: 0 0.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.nav-link i {
  font-size: 1.2rem;
  margin-right: 1rem;
  width: 20px;
  text-align: center;
}

.nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-item.active .nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0 2px 2px 0;
}

/* Footer del sidebar */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-stats {
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.stat-label {
  font-size: 0.8rem;
  opacity: 0.8;
}

.stat-value {
  font-weight: bold;
  font-size: 1rem;
}

.logout-section {
  margin-top: 1rem;
}

.logout-btn {
  width: 100%;
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.8);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 1);
  transform: translateY(-2px);
}

.logout-btn i {
  font-size: 1rem;
}

/* Footer colapsado */
.sidebar-footer-collapsed {
  padding: 1rem 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
}

.logout-btn-collapsed {
  width: 40px;
  height: 40px;
  background: rgba(239, 68, 68, 0.8);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn-collapsed:hover {
  background: rgba(239, 68, 68, 1);
  transform: scale(1.1);
}

.logout-btn-collapsed i {
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-sidebar {
    width: 70px;
  }
  
  .sidebar-collapsed {
    width: 70px;
  }
  
  .admin-details,
  .sidebar-footer {
    display: none;
  }
  
  .sidebar-footer-collapsed {
    display: flex;
  }
}

@media (max-width: 640px) {
  .dashboard-sidebar {
    width: 60px;
  }
  
  .sidebar-collapsed {
    width: 60px;
  }
  
  .admin-avatar {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .nav-link {
    padding: 0.5rem;
    margin: 0 0.25rem;
  }
  
  .nav-link i {
    font-size: 1rem;
  }
}
</style>
