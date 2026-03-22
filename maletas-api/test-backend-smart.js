const axios = require('axios');

async function testBackend() {
  const baseURL = 'http://localhost:3000/api';
  
  console.log('🧪 TESTEANDO BACKEND INTELIGENTE');
  console.log('='.repeat(50));
  
  try {
    // 1. Verificar estado inicial
    console.log('1. Estado inicial de sesión...');
    const statusResponse = await axios.get(`${baseURL}/session-status`);
    console.log('✅ Estado inicial:', statusResponse.data);

    // 2. Solo hacer login si no hay sesión activa
    if (!statusResponse.data.loggedIn) {
      console.log('2. No hay sesión activa, haciendo login...');
      const loginResponse = await axios.post(`${baseURL}/login`, {
        username: 'jp.dante.ibanez',
        password: '3981767dim'
      });
      console.log('✅ Login response:', loginResponse.data);
    } else {
      console.log('2. ✅ Sesión ya activa, omitiendo login');
    }

    // 3. Obtener datos
    console.log('3. Obteniendo datos...');
    const dataResponse = await axios.get(`${baseURL}/maletas-data`);
    console.log('✅ Datos obtenidos exitosamente!');
    console.log('   Tipo:', typeof dataResponse.data);
    console.log('   ¿Es array?:', Array.isArray(dataResponse.data));
    
    if (Array.isArray(dataResponse.data)) {
      console.log('   Número de elementos:', dataResponse.data.length);
      if (dataResponse.data.length > 0) {
        console.log('   Primer elemento:', JSON.stringify(dataResponse.data[0], null, 2));
      }
    }

    // 4. Estado final
    console.log('4. Estado final de sesión...');
    const finalStatus = await axios.get(`${baseURL}/session-status`);
    console.log('✅ Estado final:', finalStatus.data);

  } catch (error) {
    console.log('❌ Error:', error.response?.data || error.message);
    if (error.response) {
      console.log('   Status:', error.response.status);
      console.log('   Data:', error.response.data);
    }
  }
}

testBackend();