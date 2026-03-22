import { Injectable, HttpException } from '@nestjs/common';
import * as https from 'https';
import * as axios from 'axios';
import * as cheerio from 'cheerio';

@Injectable()
export class MaletasService {
  private session: any = null;
  private baseURL = 'https://maletas.oep.org.bo';

  // Agente HTTPS que ignora certificados SSL
  private httpsAgent = new https.Agent({
    rejectUnauthorized: false
  });


  private axiosInstance = axios.default.create({
    httpsAgent: this.httpsAgent,
    timeout: 30000,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    },
    maxRedirects: 5
  });

  
  async login(credentials: { username: string; password: string }) {
    try {
      console.log('🔐 Iniciando proceso de login para:', credentials.username);
      
      // Si ya hay sesión activa, verificar si sigue válida
      if (this.session?.loggedIn) {
        console.log('🔄 Sesión existente detectada, verificando validez...');
        const isValid = await this.verifySession();
        if (isValid) {
          console.log('✅ Sesión aún válida, no es necesario relogin');
          return { 
            success: true, 
            message: 'Sesión ya activa',
            sessionActive: true 
          };
        } else {
          console.log('🔄 Sesión expirada, procediendo con nuevo login');
          this.session = null;
        }
      }

      console.log('🔐 Iniciando proceso de login...');
      
      // Obtener página de login y token CSRF
      const loginPage = await this.axiosInstance.get(`${this.baseURL}/login`, {
        headers: {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
      });

      console.log('📄 Página de login obtenida, status:', loginPage.status);
      
      const csrfToken = this.extractCsrfToken(loginPage.data);
      console.log('🔄 Token CSRF encontrado:', csrfToken ? 'SI' : 'NO');

      if (!csrfToken) {
        console.log('❌ HTML recibido (primeros 500 chars):', loginPage.data.substring(0, 500));
        throw new Error('No se pudo obtener el token CSRF');
      }

      // Preparar datos para login
      const loginData = new URLSearchParams();
      loginData.append('_token', csrfToken);
      loginData.append('username', credentials.username);
      loginData.append('password', credentials.password);

      // Realizar login
      console.log('🚀 Enviando credenciales...');
      const loginResponse = await this.axiosInstance.post(
        `${this.baseURL}/login`,
        loginData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': this.baseURL,
            'Referer': `${this.baseURL}/login`,
          },
          maxRedirects: 0,
          validateStatus: (status) => status >= 200 && status < 400,
        }
      );

      console.log('📊 Respuesta login - Status:', loginResponse.status);
      console.log('📊 Respuesta login - Headers:', JSON.stringify(loginResponse.headers, null, 2));

      // Verificar si el login fue exitoso
      const redirectUrl = loginResponse.headers.location || '';
      console.log('📍 URL de redirección:', redirectUrl);

      const cookies = loginResponse.headers['set-cookie'];
      console.log('🍪 Cookies recibidas:', cookies);

      // Mejorar la verificación de login exitoso
      const loginFailed = redirectUrl.includes('/login') || 
                         !cookies || 
                         (cookies.some && cookies.some(cookie => cookie.includes('error'))) ||
                         (loginResponse.data && (
                           loginResponse.data.includes('error') ||
                           loginResponse.data.includes('invalid') ||
                           loginResponse.data.includes('incorrect')
                         ));

      if (loginFailed) {
        console.log('❌ Login falló - Redirección a login o cookies inválidas');
        if (loginResponse.data) {
          console.log('📄 Respuesta HTML (primeros 1000 chars):', loginResponse.data.substring(0, 1000));
        }
        throw new Error('Credenciales incorrectas o sesión no iniciada');
      }

      // Configurar cookies para sesiones futuras
      this.axiosInstance.defaults.headers.Cookie = cookies.join('; ');
      
      // Guardar sesión
      this.session = {
        cookies: cookies,
        credentials: credentials,
        loggedIn: true,
        loginTime: new Date()
      };

      console.log('✅ Login exitoso!');

      return { 
        success: true, 
        message: 'Login exitoso',
        redirectUrl,
        sessionActive: true
      };

    } catch (error) {
      console.error('💥 Error detallado en login:', {
        message: error.message,
        response: error.response?.data ? 'Datos en respuesta' : 'Sin datos',
        status: error.response?.status,
        headers: error.response?.headers
      });
      throw new HttpException(error.message, 500);
    }
  }

  async getMaletasData() {
    if (!this.session || !this.session.loggedIn) {
      throw new Error('No hay sesión activa. Realice login primero.');
    }

    try {
      console.log('📊 Obteniendo datos de maletas...');
      
      const response = await this.axiosInstance.get(
        `${this.baseURL}/api/custmaletas/5`,
        {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': `${this.baseURL}/`,
            'Accept': 'application/json, text/plain, */*',
          }
        }
      );

      console.log('✅ Datos obtenidos, status:', response.status);
      return response.data;

    } catch (error) {
      console.error('💥 Error obteniendo datos:', error.message);
      
      // Si el error es por sesión expirada, limpiar sesión
      if (error.response && error.response.status === 401) {
        this.session = null;
        throw new Error('Sesión expirada. Por favor, haga login nuevamente.');
      }
      
      throw new HttpException('Error obteniendo datos de maletas: ' + error.message, 500);
    }
  }

  async manualLogin(credentials: { username: string; password: string }) {
    return await this.login(credentials);
  }

  async verifySession(): Promise<boolean> {
    try {
      console.log('🔍 Verificando validez de sesión...');
      
      if (!this.session?.loggedIn) {
        console.log('❌ No hay sesión activa');
        return false;
      }
      
      const response = await this.axiosInstance.get(
        `${this.baseURL}/api/custmaletas/5`,
        {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*',
          },
          validateStatus: (status) => status < 500 // Aceptar códigos 4xx como respuesta válida
        }
      );
      
      // Considerar la sesión válida si obtenemos cualquier respuesta (incluso 401/403)
      // porque esto indica que el servidor respondió (las cookies fueron aceptadas)
      const isValid = response.status !== 404 && response.status < 500;
      
      console.log(`📊 Estado de sesión: ${isValid ? 'VÁLIDA' : 'INVÁLIDA'} (Status: ${response.status})`);
      return isValid;
      
    } catch (error) {
      console.log('❌ Error verificando sesión:', error.message);
      return false;
    }
  }

  logout() {
    this.session = null;
    this.axiosInstance.defaults.headers.Cookie = '';
    console.log('👋 Sesión cerrada');
    return { success: true, message: 'Sesión cerrada' };
  }

  getSessionStatus() {
    return {
      loggedIn: this.session?.loggedIn || false,
      username: this.session?.credentials?.username || null,
      loginTime: this.session?.loginTime || null
    };
  }

  private extractCsrfToken(html: string): string {
    try {
      const $ = cheerio.load(html);
      
      // Buscar token CSRF en input hidden
      let token = $('input[name="_token"]').val() as string;
      
      // Si no se encuentra, buscar en meta tags
      if (!token) {
        token = $('meta[name="csrf-token"]').attr('content') || '';
      }
      
      // Si aún no se encuentra, buscar en scripts
      if (!token) {
        const scriptContent = $('script').html() || '';
        const tokenMatch = scriptContent.match(/window\.csrfToken\s*=\s*['"]([^'"]+)['"]/);
        if (tokenMatch) {
          token = tokenMatch[1];
        }
      }

      console.log('🔍 Token CSRF extraído:', token ? `${token.substring(0, 20)}...` : 'NO ENCONTRADO');
      return token;

    } catch (error) {
      console.error('Error extrayendo CSRF token:', error);
      return '';
    }
  }

  /*****************************************************************
  ****** Resumen de sistema de maletas
  ***************************************************************** */

  async getResumenMaletas() {
    try {
      console.log('📊 Obteniendo resumen de maletas...');
      
      // Verificar credenciales primero
      if (!process.env.MALETAS_USERNAME || !process.env.MALETAS_PASSWORD) {
        throw new Error('Credenciales no configuradas en el servidor');
      }
      
      // Verificar y renovar sesión si es necesario
      await this.ensureValidSession();
      
      // Obtener datos de maletas
      const maletasData = await this.getMaletasData();
      this.validateMaletasDataStructure(maletasData);
      const totales = this.extractTotales(maletasData);
      return this.calculateResumen(totales);
      
    } catch (error) {
      console.error('💥 Error obteniendo resumen:', error.message);
      
      // Intentar renovar sesión y reintentar una vez
      if (error.message.includes('sesión') || error.message.includes('credenciales') || error.message.includes('activa')) {
        console.log('🔄 Reintentando con nueva sesión...');
        try {
          this.session = null; // Limpiar sesión existente
          await this.loginWithEnvCredentials();
          
          // Reintentar obtención de datos
          const maletasData = await this.getMaletasData();
          this.validateMaletasDataStructure(maletasData);
          const totales = this.extractTotales(maletasData);
          return this.calculateResumen(totales);
        } catch (retryError) {
          console.error('💥 Error en reintento:', retryError.message);
          throw new Error(`Error obteniendo resumen después de reintento: ${retryError.message}`);
        }
      }
      
      throw new Error(`Error obteniendo resumen: ${error.message}`);
    }
  }

  private async ensureValidSession(): Promise<void> {
    // Si no hay sesión, crear una nueva
    if (!this.session?.loggedIn) {
      console.log('🔐 No hay sesión activa, iniciando login automático...');
      await this.loginWithEnvCredentials();
      return;
    }
    
    // Verificar si la sesión sigue válida
    console.log('🔍 Verificando validez de sesión existente...');
    const isValid = await this.verifySession();
    
    if (!isValid) {
      console.log('🔄 Sesión expirada, renovando login...');
      this.session = null;
      await this.loginWithEnvCredentials();
    } else {
      console.log('✅ Sesión válida confirmada');
    }
  }

  private async loginWithEnvCredentials(): Promise<void> {
    const username = process.env.MALETAS_USERNAME;
    const password = process.env.MALETAS_PASSWORD;

    if (!username || !password) {
      throw new Error('Credenciales no configuradas en variables de entorno. Verifique MALETAS_USERNAME y MALETAS_PASSWORD.');
    }

    console.log(`🔐 Usando credenciales para usuario: ${username}`);
    
    const credentials = {
      username: username,
      password: password
    };

    const result = await this.login(credentials);
    
    if (!result.success) {
      throw new Error('Login automático falló: ' + (result.message || 'Error desconocido'));
    }
    
    console.log('✅ Login automático exitoso');
  }

  private validateMaletasDataStructure(data: any) {
    if (!Array.isArray(data)) {
      throw new Error('Los datos recibidos no son un array');
    }

    if (data.length < 4) {
      throw new Error('Estructura de datos incompleta');
    }

    const totalesArray = data.slice(-4);
    if (totalesArray.length !== 4 || !totalesArray.every(item => typeof item === 'number')) {
      throw new Error('Estructura de totales inválida');
    }
  }

  private extractTotales(data: any[]) {
    const totalesArray = data.slice(-4);
    return {
      TotalMesas: totalesArray[0],
      TotalProducidas: totalesArray[1],
      TotalDeueltas: totalesArray[2],
      TotalSobreA: totalesArray[3]
    };
  }

  private calculateResumen(totales: {
    TotalMesas: number;
    TotalProducidas: number;
    TotalDeueltas: number;
    TotalSobreA: number;
  }) {
    const {
      TotalMesas,
      TotalProducidas,
      TotalDeueltas,
      TotalSobreA
    } = totales;

    return {
      TotalMesas,
      TotalProducidas,
      TotalDeueltas,
      TotalSobreA,
      FaltanProducidas: TotalMesas - TotalProducidas,
      FaltanDeueltas: TotalMesas - TotalDeueltas,
      FaltanSobreA: TotalMesas - TotalSobreA
    };
  }
  

  /*****************************************************************
  ****** Resumen de sistema de monitoreo
  ***************************************************************** */

  async getReporteMonitoreo(idDepartamento: number = 5) {
    try {
      console.log('📊 Obteniendo reporte de monitoreo...');
      
      // Verificar credenciales primero
      if (!process.env.MONITOREO_USERNAME || !process.env.MONITOREO_PASSWORD) {
        throw new Error('Credenciales de monitoreo no configuradas en el servidor');
      }

      // Usaremos el mismo approach que el script Python
      const reporte = await this.obtenerReporteMonitoreoEstrategia(
        process.env.MONITOREO_USERNAME,
        process.env.MONITOREO_PASSWORD,
        idDepartamento
      );

      if (!reporte || reporte.length === 0) {
        throw new Error('No se pudo obtener el reporte de monitoreo');
      }

      console.log('✅ Reporte de monitoreo obtenido exitosamente');
      return reporte[0]; // Devolver el primer elemento del array

    } catch (error) {
      console.error('💥 Error obteniendo reporte de monitoreo:', error.message);
      throw new Error(`Error obteniendo reporte de monitoreo: ${error.message}`);
    }
  }

  private async obtenerReporteMonitoreoEstrategia(usuario: string, password: string, idDepartamento: number): Promise<any[]> {
    try {
      const https = require('https');
      const axios = require('axios');

      // Configurar agente HTTPS que ignora certificados SSL
      const httpsAgent = new https.Agent({
        rejectUnauthorized: false
      });

      const axiosInstance = axios.create({
        httpsAgent,
        timeout: 30000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
          'Accept': 'application/json, text/plain, */*',
        },
      });

      console.log('🔐 Iniciando sesión en monitoreo...');

      // 1. Login
      const dispositivo = `Web - Chrome - ${new Date().toISOString().slice(0, -5)}Z`;
      
      const loginData = {
        usuario: usuario,
        password: password,
        dispositivo: dispositivo
      };

      const loginHeaders = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://monitoreo.oep.org.bo',
        'Referer': 'https://monitoreo.oep.org.bo/login',
      };

      const loginResponse = await axiosInstance.post(
        'https://monitoreo.oep.org.bo/monitoreo_electoral/auth/login',
        loginData,
        { headers: loginHeaders }
      );

      console.log('📊 Status Login:', loginResponse.status);

      if (loginResponse.status !== 200) {
        throw new Error(`Login falló con status: ${loginResponse.status}`);
      }

      console.log('✅ Login exitoso en monitoreo');

      // 2. Extraer token de las cookies
      const cookies = loginResponse.headers['set-cookie'];
      if (cookies) {
        axiosInstance.defaults.headers.Cookie = cookies.join('; ');
      }

      // Buscar token en cookies
      let accessToken: string = '';
      if (cookies) {
        for (const cookie of cookies) {
          if (cookie.includes('access_token=')) {
            const match = cookie.match(/access_token=([^;]+)/);
            if (match && match[1]) {
              accessToken = match[1];
              break;
            }
          }
        }
      }

      // Si no se encuentra en cookies, buscar en la respuesta
      if (!accessToken) {
        const extractedToken = this.extractTokenFromResponse(loginResponse.data);
        if (extractedToken) {
          accessToken = extractedToken;
        }
      }

      if (!accessToken) {
        throw new Error('No se pudo obtener el token de acceso');
      }

      console.log('✅ Token obtenido:', accessToken ? `${accessToken.substring(0, 50)}...` : 'NO ENCONTRADO');

      // 3. Obtener reporte
      const payloadData = {
        "idPais": 32,
        "idDepartamento": idDepartamento,
        "idCircunscripcion": 0,
        "idProvincia": 0,
        "idSeccion": 0,
        "idLocalidad": 0,
        "idRecinto": 0
      };

      const reporteHeaders = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'Origin': 'https://monitoreo.oep.org.bo',
        'Referer': 'https://monitoreo.oep.org.bo/monitoreo',
      };

      console.log('📊 Solicitando reporte general...');
      console.log(`🎯 Filtros: País=32, Departamento=${idDepartamento}`);

      const reporteResponse = await axiosInstance.post(
        'https://monitoreo.oep.org.bo/monitoreo_electoral/reporte/reporteGeneral',
        payloadData,
        { headers: reporteHeaders }
      );

      console.log('📊 Status Reporte:', reporteResponse.status);

      if (reporteResponse.status === 200) {
        console.log('✅ Reporte obtenido exitosamente!');
        return reporteResponse.data;
      } else if (reporteResponse.status === 401) {
        throw new Error('Token expirado o inválido');
      } else {
        throw new Error(`Error obteniendo reporte: ${reporteResponse.status} - ${reporteResponse.data}`);
      }

    } catch (error) {
      console.error('💥 Error en estrategia de monitoreo:', error.message);
      throw error;
    }
  }

  private extractTokenFromResponse(data: any): string | null {
    try {
      // Si es string, intentar parsear como JSON
      if (typeof data === 'string') {
        try {
          data = JSON.parse(data);
        } catch (e) {
          // Si no es JSON, buscar token con regex
          const jwtPattern = /eyJhbGciOiJ[^\s"']+/;
          const matches = data.match(jwtPattern);
          if (matches && matches[0] && matches[0].length > 100) {
            return matches[0];
          }
          return null;
        }
      }

      // Si es objeto, buscar en campos comunes
      if (typeof data === 'object' && data !== null) {
        const tokenFields = ['access_token', 'token', 'accessToken', 'jwt'];
        for (const field of tokenFields) {
          if (data[field] && typeof data[field] === 'string') {
            return data[field];
          }
        }
      }

      return null;
    } catch (error) {
      console.error('Error extrayendo token:', error);
      return null;
    }
  }

  /*****************************************************************
  ****** Resumen General
  ***************************************************************** */

  async getResumenGeneral(idDepartamento: number = 5) {
    try {
      console.log('📊 Obteniendo resumen general...');
      
      // Obtener datos de ambos endpoints en paralelo para mejor performance
      const [resumenMaletas, reporteMonitoreo] = await Promise.all([
        this.getResumenMaletas().catch(error => {
          console.error('❌ Error obteniendo resumen maletas:', error.message);
          return null;
        }),
        this.getReporteMonitoreo(idDepartamento).catch(error => {
          console.error('❌ Error obteniendo reporte monitoreo:', error.message);
          return null;
        })
      ]);

      // Verificar que al menos uno de los endpoints devolvió datos
      if (!resumenMaletas && !reporteMonitoreo) {
        throw new Error('No se pudieron obtener datos de ninguno de los servicios');
      }

      // Combinar los datos en un solo objeto
      const resumenGeneral = {
        // Datos del sistema de maletas
        maletas: resumenMaletas || {
          TotalMesas: 0,
          TotalProducidas: 0,
          TotalDeueltas: 0,
          TotalSobreA: 0,
          FaltanProducidas: 0,
          FaltanDeueltas: 0,
          FaltanSobreA: 0,
          error: 'No se pudieron obtener los datos del sistema de maletas'
        },
        
        // Datos del sistema de monitoreo
        monitoreo: reporteMonitoreo || {
          agrupacion: 'N/A',
          idPaisAgrupado: 0,
          cantidadNotificacion: 0,
          cantidadCapacitacion: 0,
          cantidadEstipendio: 0,
          recepcionMaletaCdl: 0,
          resguardoMaletaRecintoElectoral: 0,
          entregaMaletaJuradoElectoral: 0,
          aperturaMesa: 0,
          cierreMesa: 0,
          noAperturaMesa: 0,
          recepcionSobreAPorNotario: 0,
          juradoSorteado: 0,
          juradoExcusado: 0,
          juradoDeLaFila: 0,
          totalEstadosJurados: 0,
          totalMaletas: 0,
          totalEtapaJuradoElegidos: 0,
          totalMesas: 0,
          usuarioRegistro: 'N/A',
          error: 'No se pudieron obtener los datos del sistema de monitoreo'
        },
        
        // Metadatos
        metadata: {
          timestamp: new Date().toISOString(),
          departamento: idDepartamento,
          fuentes: {
            maletas: !!resumenMaletas,
            monitoreo: !!reporteMonitoreo
          }
        }
      };

      console.log('✅ Resumen general obtenido exitosamente');
      return resumenGeneral;

    } catch (error) {
      console.error('💥 Error obteniendo resumen general:', error.message);
      throw new Error(`Error obteniendo resumen general: ${error.message}`);
    }
  }
}