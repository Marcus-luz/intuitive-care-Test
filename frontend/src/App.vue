<template>
  <div class="min-h-screen bg-gray-50 text-gray-800 font-sans">
    
    <div v-if="!isLoggedIn" class="min-h-screen flex items-center justify-center bg-[#f8f9fa]">
      <div class="bg-white p-10 rounded-lg shadow-xl w-[400px] text-center border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
        </div>
        
        <h1 class="text-3xl font-bold mb-2 text-gray-800">Intuitive Care</h1>
        <p class="text-gray-500 mb-8 text-sm">Acesse o portal de monitoramento da ANS</p>
        
        <button
          @click="entrar"
          class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded transition-all transform hover:-translate-y-1 hover:shadow-lg flex items-center justify-center gap-2"
        >
          <span>Entrar no Dashboard</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
          </svg>
        </button>
      </div>
    </div>

    <Dashboard v-else />

  </div>
</template>

<script setup>
import { ref } from 'vue'
// Certifique-se de que o caminho de importação do Dashboard está correto
import Dashboard from './components/Dashboard.vue'

// Estado para controlar se o usuário está "logado"
const isLoggedIn = ref(false)

const entrar = () => {
  // Em um app real, aqui chamaria a API para validar usuário e senha
  isLoggedIn.value = true
}
</script>