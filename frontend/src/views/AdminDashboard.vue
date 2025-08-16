<template>
  <div class="min-h-screen bg-cacao-pattern flex">
    <!-- Sidebar -->
    <aside class="w-16 md:w-32 bg-gradient-to-b from-green-900 to-green-700 shadow-lg flex flex-col items-center py-8 relative z-10">
      <div class="mb-10 flex flex-col items-center">
        <div class="bg-yellow-600 rounded-full p-3 mb-2 shadow-lg animate-bounce">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2C7 2 2 7 2 12c0 5 5 10 10 10s10-5 10-10c0-5-5-10-10-10zm0 0c2.5 2.5 2.5 6.5 0 9-2.5-2.5-2.5-6.5 0-9z" /></svg>
        </div>
        <span class="text-yellow-100 font-bold text-lg hidden md:block tracking-widest">CacaoScan</span>
      </div>
      <nav class="flex flex-col gap-8 mt-8 w-full items-center">
        <button class="sidebar-btn" title="Dashboard">
          <span class="text-2xl">📊</span>
          <span class="hidden">Dashboard</span>
        </button>
        <button class="sidebar-btn" title="Lotes">
          <span class="text-2xl">🌱</span>
          <span class="hidden">Lotes</span>
        </button>
        <button class="sidebar-btn" title="Análisis">
          <span class="text-2xl">🔬</span>
          <span class="hidden">Análisis</span>
        </button>
        <button class="sidebar-btn" title="Reportes">
          <span class="text-2xl">📑</span>
          <span class="hidden">Reportes</span>
        </button>
      </nav>
      <div class="mt-auto flex flex-col items-center">
        <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="avatar" class="w-10 h-10 rounded-full border-2 border-yellow-400 shadow-md" />
        <span class="text-yellow-100 text-xs mt-2 hidden md:block">Admin</span>
      </div>
    </aside>
    <!-- Main Content Wrapper -->
    <div class="flex-1 flex flex-col min-h-screen">
      <!-- Header -->
      <header class="bg-gradient-to-r from-green-700 to-green-500 shadow flex items-center justify-between px-8 py-6">
        <h1 class="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <svg xmlns='http://www.w3.org/2000/svg' class='h-8 w-8 text-yellow-400' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 2C7 2 2 7 2 12c0 5 5 10 10 10s10-5 10-10c0-5-5-10-10-10zm0 0c2.5 2.5 2.5 6.5 0 9-2.5-2.5-2.5-6.5 0-9z' /></svg>
          Panel de Administración
        </h1>
        <div class="flex items-center gap-4">
          <span class="text-white font-semibold hidden md:block">Bienvenido, Admin</span>
          <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="avatar" class="w-10 h-10 rounded-full border-2 border-yellow-400 shadow-md" />
        </div>
      </header>
      <!-- Main Content -->
      <main class="p-4 md:p-8 max-w-7xl mx-auto w-full">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3 mb-8">
          <SummaryCard 
            title="Agricultores registrados" 
            :value="'221,324'" 
            icon="👨‍🌾"
            color="green"
          />
          <SummaryCard 
            title="Lotes analizados" 
            :value="'2,324'"
            icon="🌱"
            color="emerald"
          />
          <SummaryCard 
            title="Total de análisis" 
            :value="'16,703'"
            icon="📊"
            color="lime"
          />
        </div>
        <!-- Charts and Table -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <!-- Gráfico de líneas -->
          <div class="col-span-2 bg-white p-6 rounded-xl shadow-xl border-2 border-yellow-100 animate-fade-in">
            <h2 class="text-lg font-semibold mb-4 text-green-800 flex items-center gap-2">
              <span>📈</span> Evolución de análisis 
            </h2>
            <BarChart 
              :chart-data="lineChartData"
              :chart-options="lineChartOptions"
              type="line"
              class="h-64"
            />
          </div>
          <!-- Gráfico de dona -->
          <div class="bg-white p-6 rounded-xl shadow-xl border-2 border-yellow-100 flex flex-col items-center justify-center animate-fade-in">
            <h2 class="text-lg font-semibold mb-4 text-green-800 text-center flex items-center gap-2">
              <span>🍫</span> Distribución por tipo de cacao
            </h2>
            <PieChart 
              :chart-data="doughnutChartData"
              :chart-options="doughnutChartOptions"
              class="h-64 w-full"
            />
          </div>
        </div>
        <!-- Últimos análisis realizados -->
        <div class="bg-white p-6 rounded-xl shadow-xl border-2 border-yellow-100 mb-8 animate-fade-in">
          <h2 class="text-lg font-semibold mb-4 text-green-800 flex items-center gap-2"><span>📝</span> Últimos análisis realizados</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-green-100">
              <thead>
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Agricultor</th>
                  <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Lote</th>
                  <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Defecto principal</th>
                  <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Resultado</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-green-50">
                <tr v-for="(item, idx) in paginatedAnalyses" :key="idx" class="hover:bg-green-50 transition">
                  <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.agricultor }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.lote }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.defecto }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.resultado }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Paginación simple -->
          <div class="flex justify-end mt-4 space-x-2">
            <button v-for="page in totalPages" :key="page" @click="currentPage = page" :class="['px-3 py-1 rounded font-semibold', currentPage === page ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800 hover:bg-green-200']">
              {{ page }}
            </button>
          </div>
        </div>
        <!-- Tips/Noticias -->
        <div class="bg-gradient-to-r from-yellow-100 to-green-100 border-l-4 border-yellow-400 p-6 rounded-xl shadow flex items-center gap-4 animate-fade-in">
          <span class="text-3xl">🌿</span>
          <div>
            <h3 class="font-bold text-green-900 mb-1">Tip del día</h3>
            <p class="text-green-800 text-sm">Recuerda que la calidad del grano de cacao depende en gran parte del proceso de fermentación y secado. ¡Monitorea estos pasos para obtener un producto premium!</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import SummaryCard from '@/components/dashboard/SummaryCard.vue';
import BarChart from '@/components/charts/BarChart.vue';
import PieChart from '@/components/charts/PieChart.vue';

export default {
  name: 'AdminDashboard',
  components: { SummaryCard, BarChart, PieChart },
  setup() {
    // Datos de prueba para el gráfico de líneas (evolución por tipo de defecto)
    const lineChartData = ref({
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May'],
      datasets: [
        {
          label: 'Hongos',
          data: [12, 19, 3, 5, 2],
          borderColor: '#10B981',
          backgroundColor: 'rgba(16,185,129,0.2)',
          tension: 0.4,
        },
        {
          label: 'Pizarroso',
          data: [7, 11, 5, 8, 13],
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239,68,68,0.2)',
          tension: 0.4,
        },
        {
          label: 'Planos',
          data: [9, 7, 10, 15, 8],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59,130,246,0.2)',
          tension: 0.4,
        },
        {
          label: 'Insectos',
          data: [5, 6, 7, 9, 10],
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245,158,11,0.2)',
          tension: 0.4,
        },
        {
          label: 'Violeta',
          data: [3, 4, 2, 6, 5],
          borderColor: '#8B5CF6',
          backgroundColor: 'rgba(139,92,246,0.2)',
          tension: 0.4,
        },
        {
          label: 'Dañado',
          data: [2, 3, 1, 2, 4],
          borderColor: '#F472B6',
          backgroundColor: 'rgba(244,114,182,0.2)',
          tension: 0.4,
        },
        {
          label: 'Mohoso',
          data: [1, 2, 2, 1, 3],
          borderColor: '#374151',
          backgroundColor: 'rgba(55,65,81,0.2)',
          tension: 0.4,
        },
      ],
    });
    const lineChartOptions = ref({
      responsive: true,
      plugins: {
        legend: { position: 'top' },
      },
    });

    // Datos de prueba para el gráfico de dona (tipo de cacao)
    const doughnutChartData = ref({
      labels: ['Fino aroma', 'Común', 'Híbrido'],
      datasets: [
        {
          data: [40, 30, 30],
          backgroundColor: ['#F59E0B', '#2563EB', '#10B981'],
          borderWidth: 2,
        },
      ],
    });
    const doughnutChartOptions = ref({
      responsive: true,
      cutout: '70%',
      plugins: {
        legend: { position: 'bottom' },
      },
    });

    // Datos de prueba para la tabla de últimos análisisxx
    const analyses = ref([
      { agricultor: 'Camilo Hernandez', lote: 101, defecto: 'Hongos', resultado: 'Aceptado' },
      { agricultor: 'Jeferson Alvarez', lote: 102, defecto: 'Pizarroso', resultado: 'Condicional' },
      { agricultor: 'Cristian Camacho', lote: 103, defecto: 'Planos', resultado: 'Rechazado' },
      { agricultor: 'Juan Pablo Pérez', lote: 104, defecto: 'Insectos', resultado: 'Aceptado' },
      { agricultor: 'Carlos Pérez', lote: 105, defecto: 'Violeta', resultado: 'Aceptado' },
      { agricultor: 'María Gómez', lote: 106, defecto: 'Dañado', resultado: 'Condicional' },
      { agricultor: 'Juan Torres', lote: 107, defecto: 'Mohoso', resultado: 'Rechazado' },
      { agricultor: 'Ana Ruiz', lote: 108, defecto: 'Hongos', resultado: 'Aceptado' },
    ]);
    const currentPage = ref(1);
    const pageSize = 4;
    const totalPages = computed(() => Math.ceil(analyses.value.length / pageSize));
    const paginatedAnalyses = computed(() => {
      const start = (currentPage.value - 1) * pageSize;
      return analyses.value.slice(start, start + pageSize);
    });

    return {
      lineChartData,
      lineChartOptions,
      doughnutChartData,
      doughnutChartOptions,
      analyses,
      currentPage,
      totalPages,
      paginatedAnalyses,
    };
  },
};
</script>

<style scoped>
.bg-cacao-pattern {
  background: url('https://www.transparenttextures.com/patterns/leaf.png'), linear-gradient(135deg, #f3e9e1 0%, #e6f4ea 100%);
  background-size: 200px 200px, cover;
}
.sidebar-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 0.75rem 0.5rem;
  border-radius: 0.75rem;
  transition: background 0.2s, color 0.2s, transform 0.2s;
  color: #fef9c3;
  font-weight: 600;
}
.sidebar-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fde68a;
  transform: translateY(-2px) scale(1.05);
}
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
</style>
