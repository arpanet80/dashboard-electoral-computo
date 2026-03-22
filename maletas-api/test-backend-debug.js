const axios = require('axios');

async function testBackend() {
  const baseURL = 'http://localhost:3000/api';
  
  console.log('🧪 TESTEANDO BACKEND CON DEBUG');
  console.log('='.repeat(50));
  
  try {
    // 1. Probar estado de sesión
    console.log('1. Probando estado de sesión...');
    const statusResponse = await axios.get(`${baseURL}/session-status`);
    console.log('✅ Estado de sesión:', statusResponse.data);

    // 2. Probar login
    console.log('2. Probando login...');
    const loginResponse = await axios.post(`${baseURL}/login`, {
      username: 'jp.dante.ibanez',
      password: '3981767dim'  // ⚠️ Usa la contraseña correcta
    });
    console.log('✅ Login response:', loginResponse.data);

    // 3. Probar estado de sesión después del login
    console.log('3. Estado de sesión después del login...');
    const statusAfterLogin = await axios.get(`${baseURL}/session-status`);
    console.log('✅ Estado después del login:', statusAfterLogin.data);

    // 4. Probar obtención de datos
    console.log('4. Probando obtención de datos...');
    const dataResponse = await axios.get(`${baseURL}/maletas-data`);
    console.log('✅ Datos obtenidos exitosamente!');
    console.log('   Tipo de datos:', typeof dataResponse.data);
    console.log('   ¿Es array?:', Array.isArray(dataResponse.data));
    
    if (Array.isArray(dataResponse.data)) {
      console.log('   Número de elementos:', dataResponse.data.length);
    } else if (dataResponse.data && typeof dataResponse.data === 'object') {
      console.log('   Keys del objeto:', Object.keys(dataResponse.data));
    }

  } catch (error) {
    console.log('❌ Error:', error.response?.data || error.message);
    if (error.response) {
      console.log('   Status:', error.response.status);
      console.log('   Data:', error.response.data);
    }
  }
}

testBackend();