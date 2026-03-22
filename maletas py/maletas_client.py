import requests
import json
import urllib3
from bs4 import BeautifulSoup
import getpass

urllib3.disable_warnings()

def test_different_credentials():
    """Probar diferentes formatos de credenciales"""
    
    print("🧪 PROBANDO DIFERENTES CREDENCIALES")
    print("=" * 50)
    
    # Posibles variaciones de credenciales
    test_cases = [
        {"username": "jp.dante.ibanez", "password": "3981767dim"},
        {"username": "jp.dante.ibanez", "password": "3981767DIMYLOAD"},  # Mayúsculas
        {"username": "jp.dante.ibanez", "password": "3981767"},  # Sin "dimyload"
        {"username": "jp.dante.ibanez", "password": "dimyload"},  # Solo "dimyload"
        {"username": "jp.dante.ibanez", "password": "DIMYLOAD"},  # Solo mayúsculas
    ]
    
    session = requests.Session()
    session.verify = False
    
    for i, credentials in enumerate(test_cases, 1):
        print(f"\n🔰 Prueba {i}: {credentials['username']} / {'*' * len(credentials['password'])}")
        
        # Obtener token CSRF
        login_page = session.get("https://maletas.oep.org.bo/login")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        
        if not token_input:
            print("   ❌ No se pudo obtener token CSRF")
            continue
            
        csrf_token = token_input.get('value')
        
        # Intentar login
        login_response = session.post(
            "https://maletas.oep.org.bo/login",
            data={
                '_token': csrf_token,
                'username': credentials['username'],
                'password': credentials['password']
            },
            allow_redirects=False
        )
        
        redirect_url = login_response.headers.get('Location', '')
        
        if '/login' not in redirect_url:
            print(f"   ✅ ¡POSIBLE ÉXITO! Redirige a: {redirect_url}")
            print(f"   🔑 Credenciales correctas: {credentials}")
            return credentials
        else:
            print(f"   ❌ Falló - Redirige a login")
    
    print("\n❌ Ninguna combinación funcionó")
    return None

def manual_credential_test():
    """Permitir ingresar credenciales manualmente"""
    
    print("\n👤 INGRESO MANUAL DE CREDENCIALES")
    print("=" * 40)
    
    print("NOTA: Las credenciales actuales NO funcionan")
    print("Por favor ingresa las credenciales CORRECTAS:\n")
    
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contraseña: ").strip()
    
    if not username or not password:
        print("❌ Credenciales vacías")
        return None
        
    session = requests.Session()
    session.verify = False
    
    # Probar login
    login_page = session.get("https://maletas.oep.org.bo/login")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    token_input = soup.find('input', {'name': '_token'})
    
    if not token_input:
        print("❌ Error obteniendo token CSRF")
        return None
        
    csrf_token = token_input.get('value')
    
    login_response = session.post(
        "https://maletas.oep.org.bo/login",
        data={
            '_token': csrf_token,
            'username': username,
            'password': password
        },
        allow_redirects=False
    )
    
    redirect_url = login_response.headers.get('Location', '')
    
    if '/login' not in redirect_url:
        print(f"✅ ¡CREDENCIALES CORRECTAS! Redirige a: {redirect_url}")
        
        # Seguir redirección
        session.get(redirect_url)
        
        # Obtener datos
        api_response = session.get("https://maletas.oep.org.bo/api/custmaletas/5")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print("🎉 DATOS OBTENIDOS EXITOSAMENTE!")
                return data
            except:
                print("❌ La API no devolvió JSON válido")
                return None
    else:
        print("❌ Credenciales incorrectas")
        return None

def get_data_after_successful_login(session):
    """Obtener datos después de un login exitoso"""
    
    print("\n📊 Obteniendo datos después de login exitoso...")
    
    # Headers para la API
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://maletas.oep.org.bo/'
    }
    
    api_response = session.get(
        "https://maletas.oep.org.bo/api/custmaletas/5",
        headers=headers
    )
    
    print(f"Status API: {api_response.status_code}")
    
    if api_response.status_code == 200:
        try:
            data = api_response.json()
            print("✅ Datos obtenidos exitosamente!")
            return data
        except json.JSONDecodeError:
            print("❌ La respuesta no es JSON")
            print(f"Contenido: {api_response.text[:200]}...")
            return None
    else:
        print(f"❌ Error API: {api_response.status_code}")
        return None

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("🚀 SOLUCIONADOR DE CREDENCIALES MALETAS OEP")
    print("=" * 55)
    
    # Opción 1: Probar combinaciones automáticas
    print("\n1. 🔄 Probando combinaciones automáticas...")
    working_creds = test_different_credentials()
    
    if working_creds:
        print(f"\n🎯 Credenciales que funcionan: {working_creds}")
        session = requests.Session()
        session.verify = False
        
        # Hacer login con las credenciales que funcionan
        login_page = session.get("https://maletas.oep.org.bo/login")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        csrf_token = token_input.get('value')
        
        session.post(
            "https://maletas.oep.org.bo/login",
            data={
                '_token': csrf_token,
                'username': working_creds['username'],
                'password': working_creds['password']
            },
            allow_redirects=True
        )
        
        data = get_data_after_successful_login(session)
        
    else:
        # Opción 2: Ingreso manual
        print("\n2. 👤 Ingreso manual requerido...")
        data = manual_credential_test()
    
    # Guardar datos si se obtuvieron
    if data:
        print("\n" + "="*50)
        print("💾 GUARDANDO DATOS OBTENIDOS")
        print("="*50)
        
        with open('maletas_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Datos guardados en 'maletas_data.json'")
        print(f"📊 Estructura: {type(data)}")
        
        if isinstance(data, list):
            print(f"   - Elementos: {len(data)}")
            if len(data) > 0:
                print(f"   - Fechas: {data[0]}")
                print(f"   - Primeros valores: {data[1][:5]}...")
        else:
            print(f"   - Keys: {list(data.keys())}")
    
    else:
        print("\n❌ NO SE PUDIERON OBTENER DATOS")
        print("\n🔧 RECOMENDACIONES FINALES:")
        print("   1. Verifica las credenciales en el navegador")
        print("   2. Asegúrate de que la cuenta esté activa")
        print("   3. Contacta al administrador del sistema")
        print("   4. Verifica si hay CAPTCHA o 2FA")