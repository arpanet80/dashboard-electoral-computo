import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import getpass

class MonitoreoSelenium:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configurar el driver de Chrome"""
        print("🚀 Configurando Chrome Driver...")
        
        chrome_options = Options()
        
        # Opciones para hacerlo más robusto
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Opcional: ejecutar en modo headless (sin interfaz gráfica)
        # chrome_options.add_argument('--headless')
        
        # Usar webdriver-manager para manejar automáticamente el driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configurar wait
        self.wait = WebDriverWait(self.driver, 15)
        
        print("✅ Chrome Driver configurado correctamente")
    
    def login(self, usuario, password):
        """Hacer login en el sistema"""
        print(f"🔐 Iniciando sesión para: {usuario}")
        
        try:
            # Navegar a la página de login
            self.driver.get("https://monitoreo.oep.org.bo/login")
            
            # Esperar a que cargue la página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            # Buscar campos de usuario y contraseña
            print("🔍 Buscando campos de login...")
            
            # Intentar diferentes selectores para los campos
            selectores_usuario = [
                "input[name='usuario']",
                "input[name='username']", 
                "input[type='text']",
                "input[placeholder*='usuario']",
                "input[placeholder*='Usuario']",
                "#username",
                "#usuario"
            ]
            
            selectores_password = [
                "input[name='password']",
                "input[name='clave']",
                "input[type='password']",
                "input[placeholder*='contraseña']",
                "input[placeholder*='password']",
                "#password",
                "#clave"
            ]
            
            # Encontrar campo de usuario
            campo_usuario = None
            for selector in selectores_usuario:
                try:
                    campo_usuario = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Campo usuario encontrado con: {selector}")
                    break
                except:
                    continue
            
            # Encontrar campo de password
            campo_password = None
            for selector in selectores_password:
                try:
                    campo_password = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Campo password encontrado con: {selector}")
                    break
                except:
                    continue
            
            if not campo_usuario or not campo_password:
                print("❌ No se pudieron encontrar los campos de login")
                # Tomar screenshot para debug
                self.driver.save_screenshot('login_page.png')
                print("📸 Screenshot guardado como 'login_page.png'")
                return False
            
            # Limpiar y llenar campos
            campo_usuario.clear()
            campo_usuario.send_keys(usuario)
            
            campo_password.clear()
            campo_password.send_keys(password)
            
            # Buscar y hacer click en el botón de login
            print("🔍 Buscando botón de login...")
            
            selectores_boton = [
                "button[type='submit']",
                "input[type='submit']",
                "button.btn-primary",
                "button.btn",
                ".btn-primary",
                ".btn-login",
                "button"
            ]
            
            boton_login = None
            for selector in selectores_boton:
                try:
                    boton_login = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Botón login encontrado con: {selector}")
                    break
                except:
                    continue
            
            if not boton_login:
                print("❌ No se pudo encontrar ningún botón")
                return False
            
            # Hacer click en el botón
            boton_login.click()
            print("✅ Click en botón de login realizado")
            
            # Esperar a que se procese el login
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            print(f"📄 URL actual: {current_url}")
            
            # Verificar si hay mensaje de error
            try:
                mensaje_error = self.driver.find_element(By.CSS_SELECTOR, ".error, .alert-danger, .text-danger, .login-error")
                print(f"❌ Error de login: {mensaje_error.text}")
                return False
            except:
                pass
            
            if "login" in current_url:
                print("❌ Login falló - aún en página de login")
                return False
            else:
                print("✅ Login exitoso - redirigido a otra página")
                return True
                
        except Exception as e:
            print(f"❌ Error durante el login: {e}")
            # Tomar screenshot para debug
            self.driver.save_screenshot('login_error.png')
            print("📸 Screenshot del error guardado como 'login_error.png'")
            return False
    
    def obtener_datos_via_api(self):
        """Obtener datos directamente via API usando JavaScript"""
        print("🔧 Ejecutando petición API via JavaScript...")
        
        try:
            script = """
            return new Promise((resolve, reject) => {
                const payload = {
                    idPais: 32,
                    idDepartamento: 5,
                    idCircunscripcion: 0,
                    idProvincia: 0,
                    idSeccion: 0,
                    idLocalidad: 0,
                    idRecinto: 0
                };
                
                fetch('/monitoreo_electoral/reporte/reporteGeneral', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error ' + response.status);
                    }
                    return response.json();
                })
                .then(data => resolve(data))
                .catch(error => reject(error));
            });
            """
            
            # Ejecutar el script con timeout
            datos = self.driver.execute_async_script(script)
            print("✅ Datos obtenidos via API")
            return datos
            
        except Exception as e:
            print(f"❌ Error en petición API: {e}")
            return None
    
    def obtener_datos_desde_pagina(self):
        """Buscar datos en el HTML de la página"""
        print("🔍 Buscando datos en la página...")
        
        try:
            # Buscar elementos que puedan contener los datos
            selectores = [
                ".datos-monitoreo",
                "[data-reporte]",
                ".reporte-data",
                ".tabla-datos",
                "table",
                "pre"
            ]
            
            for selector in selectores:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elemento in elementos:
                        texto = elemento.text
                        if texto and len(texto) > 100:  # Si tiene suficiente texto
                            print(f"✅ Datos encontrados con selector: {selector}")
                            # Intentar parsear como JSON
                            try:
                                # Limpiar el texto y buscar JSON
                                lines = texto.split('\\n')
                                for line in lines:
                                    if line.strip().startswith('{') or line.strip().startswith('['):
                                        return json.loads(line.strip())
                            except:
                                return texto
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error buscando datos en página: {e}")
            return None
    
    def close(self):
        """Cerrar el navegador"""
        if self.driver:
            print("🔒 Cerrando navegador...")
            self.driver.quit()

def main():
    print("🚀 MONITOREO OEP CON SELENIUM")
    print("=" * 40)
    
    # Credenciales
    usuario = "dante.ibanez"  # o usa input() si prefieres
    password = "Electoral2025"
    
    # usuario = input("Usuario: ").strip()
    # password = getpass.getpass("Contraseña: ").strip()
    
    if not usuario or not password:
        print("❌ Credenciales vacías")
        return
    
    # Inicializar Selenium
    monitoreo = MonitoreoSelenium()
    
    try:
        # Configurar driver
        monitoreo.setup_driver()
        
        # Hacer login
        if monitoreo.login(usuario, password):
            print("\\n✅ Login exitoso, obteniendo datos...")
            
            # Esperar a que la página cargue completamente
            time.sleep(5)
            
            # Estrategia 1: Obtener datos via API
            print("\\n🎯 Estrategia 1: Obteniendo datos via API...")
            datos = monitoreo.obtener_datos_via_api()
            
            if not datos:
                # Estrategia 2: Buscar datos en la página
                print("\\n🎯 Estrategia 2: Buscando datos en la página...")
                datos = monitoreo.obtener_datos_desde_pagina()
            
            if datos:
                print("\\n" + "="*50)
                print("💾 DATOS OBTENIDOS EXITOSAMENTE!")
                print("="*50)
                
                # Guardar datos
                with open('monitoreo_data_selenium.json', 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)
                
                print("✅ Datos guardados en 'monitoreo_data_selenium.json'")
                
                # Mostrar datos importantes
                if isinstance(datos, list) and len(datos) > 0:
                    primer_item = datos[0]
                    print(f"📊 RESUMEN:")
                    print(f"   - Agrupación: {primer_item.get('agrupacion', 'N/A')}")
                    print(f"   - Total Mesas: {primer_item.get('totalMesas', 'N/A')}")
                    print(f"   - Apertura Mesa: {primer_item.get('aperturaMesa', 'N/A')}")
                    print(f"   - Recepción Maletas: {primer_item.get('recepcionMaletaCdl', 'N/A')}")
                else:
                    print(f"📊 Datos: {datos}")
            else:
                print("\\n❌ No se pudieron obtener los datos automáticamente")
                print("💡 Guardando HTML de la página para análisis...")
                
                # Guardar el HTML de la página
                html = monitoreo.driver.page_source
                with open('monitoreo_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("✅ HTML guardado en 'monitoreo_page.html'")
                
                # Guardar screenshot
                monitoreo.driver.save_screenshot('monitoreo_page.png')
                print("✅ Screenshot guardado en 'monitoreo_page.png'")
                
        else:
            print("❌ No se pudo hacer login")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Esperar antes de cerrar
        print("\\n⏳ El navegador se cerrará en 10 segundos...")
        time.sleep(10)
        monitoreo.close()

if __name__ == "__main__":
    main()