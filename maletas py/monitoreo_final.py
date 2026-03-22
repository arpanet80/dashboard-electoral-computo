import requests
import json
import urllib3
from datetime import datetime, timezone
import getpass
import re

urllib3.disable_warnings()

class MonitoreoClient:
    def __init__(self):
        self.base_url = "https://monitoreo.oep.org.bo"
        self.session = requests.Session()
        self.session.verify = False
        self.access_token = None
    
    def login(self, usuario, password):
        """Login al sistema y obtener token fresco"""
        print("🔐 Iniciando sesión...")
        
        # Primero, hacer una petición GET a la página de login para obtener posibles tokens CSRF
        print("📄 Obteniendo página de login...")
        try:
            login_page = self.session.get(f"{self.base_url}/login")
            # Buscar tokens en la página
            tokens = self._find_tokens_in_html(login_page.text)
            if tokens:
                print(f"🔍 Tokens encontrados en página: {list(tokens.keys())}")
        except:
            pass
        
        dispositivo = f"Web - Chrome - {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
        
        login_data = {
            "usuario": usuario,
            "password": password,
            "dispositivo": dispositivo
        }
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/login',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        }
        
        response = self.session.post(
            f"{self.base_url}/monitoreo_electoral/auth/login",
            json=login_data,
            headers=headers
        )
        
        print(f"Status Login: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login exitoso")
            
            # Buscar token en la respuesta del login
            token_encontrado = self._extract_token_from_response(response)
            if token_encontrado:
                self.access_token = token_encontrado
                print("✅ Token encontrado en respuesta de login")
                return True
            
            # Si no está en la respuesta, intentar obtenerlo de las cookies o haciendo otra petición
            return self._obtain_token_after_login()
        else:
            try:
                error_data = response.json()
                print(f"❌ Error en login: {error_data.get('mensaje', 'Error desconocido')}")
            except:
                print(f"❌ Error en login: {response.status_code} - {response.text}")
            return False
    
    def _extract_token_from_response(self, response):
        """Extraer token de diferentes lugares en la respuesta"""
        # Buscar en el cuerpo de la respuesta
        try:
            response_data = response.json()
            if isinstance(response_data, dict):
                # Buscar en campos comunes de token
                for key in ['access_token', 'token', 'accessToken', 'jwt']:
                    if key in response_data and response_data[key]:
                        return response_data[key]
        except:
            pass
        
        # Buscar en headers
        if 'Authorization' in response.headers:
            auth_header = response.headers['Authorization']
            if auth_header.startswith('Bearer '):
                return auth_header.replace('Bearer ', '')
        
        # Buscar en el texto usando regex para JWT
        jwt_pattern = r'eyJhbGciOiJ[^\s"\']+'
        matches = re.findall(jwt_pattern, response.text)
        for match in matches:
            if len(match) > 100:  # Los JWT son largos
                return match
        
        return None
    
    def _find_tokens_in_html(self, html):
        """Buscar tokens en HTML"""
        tokens = {}
        
        # Buscar JWT
        jwt_matches = re.findall(r'eyJhbGciOiJ[^\s"\']+', html)
        for i, token in enumerate(jwt_matches):
            if len(token) > 100:
                tokens[f'jwt_{i}'] = token
        
        # Buscar en meta tags
        meta_pattern = r'<meta[^>]+(name|property)="([^"]*token[^"]*)"[^>]+content="([^"]+)"'
        meta_matches = re.findall(meta_pattern, html, re.IGNORECASE)
        for match in meta_matches:
            tokens[f'meta_{match[1]}'] = match[2]
        
        return tokens
    
    def _obtain_token_after_login(self):
        """Intentar obtener el token después del login haciendo peticiones a rutas protegidas"""
        print("🔍 Buscando token después del login...")
        
        # Intentar diferentes endpoints que podrían devolver el token
        endpoints = [
            f"{self.base_url}/monitoreo_electoral/user/info",
            f"{self.base_url}/monitoreo_electoral/auth/me", 
            f"{self.base_url}/monitoreo_electoral/auth/user",
            f"{self.base_url}/monitoreo_electoral/dashboard",
        ]
        
        for endpoint in endpoints:
            print(f"🔍 Probando endpoint: {endpoint}")
            try:
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
                }
                
                response = self.session.get(endpoint, headers=headers)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    token = self._extract_token_from_response(response)
                    if token:
                        self.access_token = token
                        print(f"✅ Token encontrado en {endpoint}")
                        return True
                    
                    # Si el endpoint devuelve datos de usuario, tal vez el token está en otro lado
                    try:
                        user_data = response.json()
                        print(f"   Datos usuario: {user_data}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   Error: {e}")
        
        print("❌ No se pudo obtener token automáticamente")
        return False
    
    def obtener_reporte_con_token_fresco(self):
        """Estrategia: Hacer una petición inicial para forzar la generación del token"""
        print("🔄 Intentando obtener token fresco...")
        
        # Primero navegar a la página principal después del login
        try:
            print("📄 Navegando a página de monitoreo...")
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
            }
            response = self.session.get(f"{self.base_url}/monitoreo", headers=headers)
            print(f"Status Monitoreo: {response.status_code}")
            
            # Buscar token en esta respuesta
            token = self._extract_token_from_response(response)
            if token:
                self.access_token = token
                print("✅ Token encontrado en página de monitoreo")
                return True
                
        except Exception as e:
            print(f"❌ Error navegando a monitoreo: {e}")
        
        return False
    
    def obtener_reporte_filtrado(self, id_departamento=5):
        """Obtener reporte con filtros aplicados"""
        
        # Si no tenemos token, intentar obtenerlo fresco
        if not self.access_token:
            print("⚠️  No hay token, intentando obtener uno fresco...")
            if not self.obtener_reporte_con_token_fresco():
                print("❌ No se pudo obtener token")
                return None
        
        # Payload para Potosí
        payload_data = {
            "idPais": 32,
            "idDepartamento": id_departamento,
            "idCircunscripcion": 0,
            "idProvincia": 0,
            "idSeccion": 0,
            "idLocalidad": 0,
            "idRecinto": 0
        }
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/monitoreo',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        }
        
        print("📊 Solicitando reporte general...")
        print(f"🎯 Filtros: País=32, Departamento={id_departamento}")
        print(f"🔑 Token usado: {self.access_token[:50]}...")
        
        response = self.session.post(
            f"{self.base_url}/monitoreo_electoral/reporte/reporteGeneral",
            json=payload_data,
            headers=headers
        )
        
        print(f"Status Reporte: {response.status_code}")
        
        if response.status_code == 200:
            datos = response.json()
            print("✅ Reporte obtenido exitosamente!")
            return datos
        elif response.status_code == 401:
            print("❌ Token expirado o inválido")
            print("💡 Intentando regenerar token...")
            # Si el token expiró, intentar obtener uno nuevo
            self.access_token = None
            if self.obtener_reporte_con_token_fresco():
                return self.obtener_reporte_filtrado(id_departamento)
            else:
                return None
        else:
            print(f"❌ Error obteniendo reporte: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None

# ESTRATEGIA ALTERNATIVA: Usar el mismo approach que el navegador
def estrategia_navegador_simulation():
    """Simular exactamente lo que hace el navegador"""
    print("\n🔄 ESTRATEGIA ALTERNATIVA: Simulación de navegador")
    
    session = requests.Session()
    session.verify = False
    
    # 1. Login
    print("1. 🔐 Haciendo login...")
    dispositivo = f"Web - Chrome - {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
    
    login_data = {
        "usuario": "dante.ibanez",
        "password": "Electoral2025",
        "dispositivo": dispositivo
    }
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://monitoreo.oep.org.bo',
        'Referer': 'https://monitoreo.oep.org.bo/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }
    
    response = session.post(
        "https://monitoreo.oep.org.bo/monitoreo_electoral/auth/login",
        json=login_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print("❌ Login falló")
        return None
    
    print("✅ Login exitoso")
    
    # 2. Extraer el access_token de LAS COOKIES (no del header)
    print("2. 🔍 Buscando token en cookies...")
    
    # Listar todas las cookies
    print("🍪 Cookies disponibles:")
    for cookie in session.cookies:
        print(f"   - {cookie.name}: {cookie.value[:50]}...")
    
    # El token podría estar en una cookie llamada 'access_token' o similar
    access_token_cookie = session.cookies.get('access_token') or session.cookies.get('token')
    
    if access_token_cookie:
        print(f"✅ Token encontrado en cookie: {access_token_cookie[:50]}...")
        token = access_token_cookie
    else:
        print("❌ No se encontró token en cookies")
        return None
    
    # 3. Hacer la petición del reporte
    print("3. 📊 Obteniendo reporte...")
    
    payload_data = {
        "idPais": 32,
        "idDepartamento": 5,
        "idCircunscripcion": 0,
        "idProvincia": 0,
        "idSeccion": 0,
        "idLocalidad": 0,
        "idRecinto": 0
    }
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Origin': 'https://monitoreo.oep.org.bo',
        'Referer': 'https://monitoreo.oep.org.bo/monitoreo',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }
    
    response = session.post(
        "https://monitoreo.oep.org.bo/monitoreo_electoral/reporte/reporteGeneral",
        json=payload_data,
        headers=headers
    )
    
    print(f"Status Reporte: {response.status_code}")
    
    if response.status_code == 200:
        datos = response.json()
        print("✅ Reporte obtenido exitosamente!")
        return datos
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

# USO
if __name__ == "__main__":
    print("🚀 CLIENTE MONITOREO OEP - ESTRATEGIA MEJORADA")
    print("=" * 55)
    
    # Probar estrategia principal primero
    client = MonitoreoClient()
    
    if client.login("dante.ibanez", "Electoral2025"):
        print("\n" + "="*50)
        print("✅ LOGIN EXITOSO - OBTENIENDO DATOS")
        print("="*50)
        
        datos = client.obtener_reporte_filtrado(5)
        
        if datos:
            print("✅ Datos obtenidos:")
            print(json.dumps(datos, indent=2, ensure_ascii=False))
            
            with open('datos_potosi.json', 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            print("💾 Datos guardados en 'datos_potosi.json'")
        else:
            print("\n❌ La estrategia principal falló, probando alternativa...")
            
            # Probar estrategia alternativa
            datos = estrategia_navegador_simulation()
            if datos:
                print("✅ ¡Estrategia alternativa funcionó!")
                print(json.dumps(datos, indent=2, ensure_ascii=False))
                
                with open('datos_potosi_alternativo.json', 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)
                print("💾 Datos guardados en 'datos_potosi_alternativo.json'")
            else:
                print("❌ Ninguna estrategia funcionó")
    else:
        print("❌ No se pudo hacer login")