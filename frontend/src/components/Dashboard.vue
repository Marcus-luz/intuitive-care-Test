<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { 
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale 
} from 'chart.js';

// Registro obrigatório dos componentes do Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);


// --- ESTADOS DA TABELA PRINCIPAL ---
const operadoras = ref([]);
const total = ref(0);
const page = ref(1);
const limit = 10;
const search = ref("");
const loading = ref(false);
const error = ref(null);

// --- ESTADOS DO GRÁFICO ---
const chartData = ref({ labels: [], datasets: [] });
const chartOptions = { responsive: true, maintainAspectRatio: false };
const statsLoaded = ref(false);

// --- ESTADOS DE DETALHES ---
const operadoraSelecionada = ref(null);
const historico = ref([]);
const loadingDetalhes = ref(false);

// 4.2.1 Rota: Listagem e Busca no Servidor (Ajustado para o seu banco)
const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const res = await fetch(`http://localhost:8000/api/operadoras?page=${page.value}&limit=${limit}&q=${search.value}`);
    if (!res.ok) throw new Error("Erro ao conectar com o servidor");
    
    const result = await res.json();
    operadoras.value = result.data;
    total.value = result.total;
  } catch (err) {
    error.value = "Não foi possível carregar a lista de operadoras. Verifique se o Backend está ativo.";
  } finally {
    loading.value = false;
  }
};

// 4.2.4 Rota: Estatísticas para o Gráfico
const fetchStats = async () => {
  try {
    const res = await fetch(`http://localhost:8000/api/estatisticas`);
    const data = await res.json();
    
    chartData.value = {
      labels: data.uf_distribution.map(i => i.uf),
      datasets: [{
        label: 'Distribuição de Despesas por UF (R$)',
        backgroundColor: '#42b883',
        data: data.uf_distribution.map(i => i.despesa_uf)
      }]
    };
    statsLoaded.value = true;
  } catch (err) {
    console.error("Erro ao carregar estatísticas do gráfico");
  }
};

// --- FUNÇÕES DE DETALHES (AJUSTE CRÍTICO: Usando Razão Social como ID) ---
const verDetalhes = async (op) => {
  operadoraSelecionada.value = op;
  loadingDetalhes.value = true;
  try {
    // Usamos encodeURIComponent porque a Razão Social contém espaços e caracteres especiais
    const id = encodeURIComponent(op.razao_social);
    const res = await fetch(`http://localhost:8000/api/operadoras/historico/${id}`);
    historico.value = await res.json();
  } catch (err) {
    console.error("Erro ao carregar histórico");
  } finally {
    loadingDetalhes.value = false;
  }
};

const voltar = () => {
  operadoraSelecionada.value = null;
  historico.value = [];
};

// --- CICLO DE VIDA E WATCHERS ---
onMounted(() => {
  fetchData();
  fetchStats();
});

watch(search, () => {
  page.value = 1;
  fetchData();
});

watch(page, fetchData);

const totalPages = computed(() => Math.ceil(total.value / limit));

// Formatador de moeda
const formatCurrency = (val) => {
  return Number(val).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};
</script>

<template>
  <div class="p-8 max-w-7xl mx-auto bg-gray-50 min-h-screen">
    
    <div v-if="!operadoraSelecionada">
      <h1 class="text-3xl font-bold text-gray-800 mb-8">Dashboard de Operadoras - Intuitive Care</h1>

      <div class="mb-6">
        <input 
          v-model="search" 
          type="text"
          placeholder="🔍 Buscar por Razão Social..." 
          class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 bg-white p-6 rounded-xl shadow-md">
          <h2 class="text-xl font-semibold mb-4 border-b pb-2">Lista de Operadoras</h2>
          
          <div v-if="loading" class="flex justify-center my-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="error" class="p-4 mb-4 text-red-700 bg-red-100 rounded-lg">
            {{ error }}
          </div>

          <div v-else-if="operadoras.length === 0" class="text-center py-10 text-gray-500">
            Nenhuma operadora encontrada para o termo "{{ search }}".
          </div>

          <div v-else>
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-gray-100 text-gray-600 uppercase text-xs">
                    <th class="p-3 border-b">ID</th>
                    <th class="p-3 border-b">Razão Social</th>
                    <th class="p-3 border-b text-center">UF</th>
                    <th class="p-3 border-b text-right">Ações</th>
                  </tr>
                </thead>
                <tbody class="text-gray-700 text-sm">
                  <tr v-for="op in operadoras" :key="op.id" class="hover:bg-blue-50 transition-colors">
                    <td class="p-3 border-b text-gray-400">#{{ op.id }}</td>
                    <td class="p-3 border-b font-medium">{{ op.razao_social }}</td>
                    <td class="p-3 border-b text-center">{{ op.uf }}</td>
                    <td class="p-3 border-b text-right">
                      <button @click="verDetalhes(op)" class="text-blue-600 hover:underline font-semibold">
                        Ver Histórico
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex items-center justify-between mt-6">
              <button @click="page--" :disabled="page <= 1" class="px-4 py-2 bg-gray-200 rounded-md disabled:opacity-50 hover:bg-gray-300 transition">
                Anterior
              </button>
              <span class="text-sm font-medium text-gray-600">Página {{ page }} de {{ totalPages }}</span>
              <button @click="page++" :disabled="page >= totalPages" class="px-4 py-2 bg-gray-200 rounded-md disabled:opacity-50 hover:bg-gray-300 transition">
                Próxima
              </button>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-xl shadow-md h-fit">
          <h2 class="text-xl font-semibold mb-4 border-b pb-2">Distribuição Geográfica</h2>
          <div class="h-64">
            <Bar v-if="statsLoaded" :data="chartData" :options="chartOptions" />
            <div v-else class="h-full flex items-center justify-center text-gray-400">Carregando estatísticas...</div>
          </div>
          <p class="text-xs text-gray-500 mt-4 italic">* Valores baseados nas despesas agregadas por estado.</p>
        </div>
      </div>
    </div>

    <div v-else class="bg-white p-8 rounded-xl shadow-lg animate-fade-in">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 border-b pb-6">
        <div>
          <button @click="voltar" class="text-blue-500 hover:text-blue-700 mb-2 font-medium flex items-center gap-1">
            ← Voltar para a lista
          </button>
          <h2 class="text-3xl font-bold text-gray-800">{{ operadoraSelecionada.razao_social }}</h2>
          <div class="flex gap-4 mt-2">
            <span class="bg-gray-100 px-3 py-1 rounded text-sm text-gray-600">UF: {{ operadoraSelecionada.uf }}</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="border rounded-xl overflow-hidden shadow-sm">
          <table class="w-full text-left">
            <thead class="bg-gray-50 border-b">
              <tr>
                <th class="p-4 font-semibold text-gray-600">Ano / Trimestre</th>
                <th class="p-4 font-semibold text-gray-600 text-right">Valor da Despesa</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loadingDetalhes">
                <td colspan="2" class="p-8 text-center text-blue-500">Carregando histórico...</td>
              </tr>
              <tr v-for="item in historico" :key="item.id" class="border-t hover:bg-gray-50">
                <td class="p-4">{{ item.ano }} - {{ item.trimestre }}º Trimestre</td>
                <td class="p-4 text-right font-mono font-bold">{{ formatCurrency(item.valor_despesa) }}</td>
              </tr>
              <tr v-if="!loadingDetalhes && historico.length === 0">
                <td colspan="2" class="p-8 text-center text-gray-400">Nenhum histórico encontrado para esta operadora.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="space-y-6">
          <div class="bg-blue-50 p-6 rounded-xl border border-blue-100">
            <h3 class="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
              📊 Resumo da Operadora
            </h3>
            <div class="space-y-4">
              <div class="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span class="text-gray-600">Gasto Total Acumulado:</span>
                <span class="text-xl font-bold text-gray-900">{{ formatCurrency(operadoraSelecionada.total_despesas) }}</span>
              </div>
              <div class="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span class="text-gray-600">Média Trimestral:</span>
                <span class="text-xl font-bold text-green-600">{{ formatCurrency(operadoraSelecionada.media_trimestral) }}</span>
              </div>
              <div class="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span class="text-gray-600">Desvio Padrão:</span>
                <span class="text-xl font-bold text-orange-500">{{ formatCurrency(operadoraSelecionada.desvio_padrao) }}</span>
              </div>
            </div>
          </div>
          
          <div class="p-4 bg-yellow-50 border border-yellow-100 rounded-lg text-sm text-yellow-800">
            <strong>Nota técnica:</strong> Estas métricas foram pré-calculadas durante o pipeline de ETL e persistidas para alta performance da API.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>