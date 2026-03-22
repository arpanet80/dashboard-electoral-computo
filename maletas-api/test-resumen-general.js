const axios = require('axios');

async function testResumenGeneral() {
  const baseURL = 'http://localhost:3000/api';
  
  console.log('🧪 TESTEANDO ENDPOINT RESUMEN GENERAL');
  console.log('='.repeat(50));
  
  try {
    console.log('1. Obteniendo resumen general...');
    const response = await axios.get(`${baseURL}/resumen-general?departamento=5`);
    
    console.log('✅ Resumen general obtenido exitosamente!');
    console.log('   Success:', response.data.success);
    console.log('   Message:', response.data.message);
    
    // Verificar estructura del response
    const data = response.data.data;
    console.log('   Estructura del resumen:');
    console.log('   - Maletas:', data.maletas ? '✓ Datos disponibles' : '✗ Sin datos');
    console.log('   - Monitoreo:', data.monitoreo ? '✓ Datos disponibles' : '✗ Sin datos');
    console.log('   - Metadata:', data.metadata.timestamp);
    
    // Mostrar algunos datos clave
    if (data.maletas && !data.maletas.error) {
      console.log('\n   📦 DATOS MALETAS:');
      console.log('      Total Mesas:', data.maletas.TotalMesas);
      console.log('      Producidas:', data.maletas.TotalProducidas);
      console.log('      Deueltas:', data.maletas.TotalDeueltas);
      console.log('      Sobre A:', data.maletas.TotalSobreA);
    }
    
    if (data.monitoreo && !data.monitoreo.error) {
      console.log('\n   📊 DATOS MONITOREO:');
      console.log('      Agrupación:', data.monitoreo.agrupacion);
      console.log('      Apertura Mesa:', data.monitoreo.aperturaMesa);
      console.log('      Cierre Mesa:', data.monitoreo.cierreMesa);
      console.log('      Recepción Sobre A:', data.monitoreo.recepcionSobreAPorNotario);
    }
    
  } catch (error) {
    console.log('❌ Error:', error.response?.data || error.message);
    if (error.response) {
      console.log('   Status:', error.response.status);
      console.log('   Error Code:', error.response.data.error);
      console.log('   Message:', error.response.data.message);
    }
  }
}

testResumenGeneral();