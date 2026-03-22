const axios = require('axios');

async function testResumenMaletas() {
  const baseURL = 'http://localhost:3000/api';
  
  console.log('🧪 TESTEANDO ENDPOINT RESUMEN MALETAS');
  console.log('='.repeat(50));
  
  try {
    console.log('1. Obteniendo resumen de maletas...');
    const response = await axios.get(`${baseURL}/resumen-maletas`);
    
    console.log('✅ Resumen obtenido exitosamente!');
    console.log('   Success:', response.data.success);
    console.log('   Message:', response.data.message);
    console.log('   Data:', JSON.stringify(response.data.data, null, 2));
    
    // Verificar estructura del response
    const requiredFields = [
      'TotalMesas', 'TotalProducidas', 'TotalDeueltas', 'TotalSobreA',
      'FaltanProducidas', 'FaltanDeueltas', 'FaltanSobreA'
    ];
    
    const hasAllFields = requiredFields.every(field => field in response.data.data);
    console.log('   Estructura válida:', hasAllFields);
    
  } catch (error) {
    console.log('❌ Error:', error.response?.data || error.message);
    if (error.response) {
      console.log('   Status:', error.response.status);
      console.log('   Error Code:', error.response.data.error);
      console.log('   Message:', error.response.data.message);
    }
  }
}

testResumenMaletas();