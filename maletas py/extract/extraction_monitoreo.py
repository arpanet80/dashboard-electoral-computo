import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import getpass
from bs4 import BeautifulSoup

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
            
            # Encontrar campo de usuario
            campo_usuario = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            print("✅ Campo usuario encontrado")
            
            # Encontrar campo de password
            campo_password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            print("✅ Campo password encontrado")
            
            # Limpiar y llenar campos
            campo_usuario.clear()
            campo_usuario.send_keys(usuario)
            
            campo_password.clear()
            campo_password.send_keys(password)
            
            # Buscar y hacer click en el botón de login
            boton_login = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            print("✅ Botón login encontrado")
            
            # Hacer click en el botón
            boton_login.click()
            print("✅ Click en botón de login realizado")
            
            # Esperar a que se procese el login
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            print(f"📄 URL actual: {current_url}")
            
            if "login" in current_url:
                print("❌ Login falló - aún en página de login")
                return False
            else:
                print("✅ Login exitoso - redirigido a otra página")
                return True
                
        except Exception as e:
            print(f"❌ Error durante el login: {e}")
            return False

    def aplicar_filtros_geograficos(self):
        """Aplicar los filtros geográficos: Nacional (Bolivia) y Potosí"""
        print("🗺️ Aplicando filtros geográficos...")
        
        try:
            # Esperar a que la página cargue completamente
            time.sleep(3)
            
            # Tomar screenshot antes de aplicar filtros
            self.driver.save_screenshot('antes_filtros.png')
            print("📸 Screenshot antes de filtros: 'antes_filtros.png'")
            
            # Buscar los selects de filtros geográficos
            print("🔍 Buscando selects de filtros...")
            
            # Intentar diferentes selectores para los filtros
            selectores_filtros = [
                "select",
                ".filtro-select",
                "[id*='filtro']",
                "[name*='filtro']",
                "mat-select",  # Por si usa Angular Material
                "p-dropdown"   # Por si usa PrimeNG
            ]
            
            selects = []
            for selector in selectores_filtros:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    selects.extend(elementos)
                    if elementos:
                        print(f"✅ Encontrados {len(elementos)} elementos con selector: {selector}")
                except:
                    continue
            
            print(f"🔍 Total de selects encontrados: {len(selects)}")
            
            # Si encontramos al menos 2 selects, intentar usarlos
            if len(selects) >= 2:
                print("🎯 Intentando seleccionar 'Nacional (Bolivia)' en el primer select...")
                
                # Primer select - Nacional (Bolivia)
                try:
                    select1 = Select(selects[0])
                    # Intentar seleccionar por texto visible
                    select1.select_by_visible_text("Nacional (Bolivia)")
                    print("✅ 'Nacional (Bolivia)' seleccionado")
                    time.sleep(2)
                except:
                    print("❌ No se pudo seleccionar 'Nacional (Bolivia)' por texto, intentando alternativas...")
                    # Intentar otras opciones
                    try:
                        select1.select_by_index(0)  # Primera opción
                        print("✅ Seleccionada primera opción")
                    except:
                        print("❌ No se pudo seleccionar primera opción")
                
                # Segundo select - Potosí
                print("🎯 Intentando seleccionar 'Potosí' en el segundo select...")
                try:
                    select2 = Select(selects[1])
                    select2.select_by_visible_text("Potosí")
                    print("✅ 'Potosí' seleccionado")
                    time.sleep(2)
                except:
                    print("❌ No se pudo seleccionar 'Potosí' por texto, intentando alternativas...")
                    try:
                        # Buscar Potosí en las opciones disponibles
                        for option in select2.options:
                            if "Potosí" in option.text or "Potos" in option.text:
                                select2.select_by_visible_text(option.text)
                                print(f"✅ Seleccionado: {option.text}")
                                break
                    except:
                        print("❌ No se pudo seleccionar Potosí")
            
            # Esperar a que se actualicen los datos después de aplicar filtros
            print("⏳ Esperando a que se actualicen los datos con los filtros...")
            time.sleep(5)
            
            # Tomar screenshot después de aplicar filtros
            self.driver.save_screenshot('despues_filtros.png')
            print("📸 Screenshot después de filtros: 'despues_filtros.png'")
            
            return True
            
        except Exception as e:
            print(f"❌ Error aplicando filtros: {e}")
            # Tomar screenshot del error
            self.driver.save_screenshot('error_filtros.png')
            return False

    def buscar_y_aplicar_filtros_avanzado(self):
        """Búsqueda más avanzada de los filtros geográficos"""
        print("🔍 Búsqueda avanzada de filtros...")
        
        try:
            # Buscar por texto en la página que indique los filtros
            textos_filtro = ["Filtros Geográficos", "FILTROS GEOGRÁFICOS", "Filtros", "Departamento", "Nacional"]
            
            for texto in textos_filtro:
                try:
                    elemento = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{texto}')]")
                    print(f"✅ Encontrado texto: '{texto}'")
                    
                    # Buscar selects cerca de este elemento
                    selects_cercanos = elemento.find_elements(By.XPATH, "./following::select | ./preceding::select")
                    if selects_cercanos:
                        print(f"✅ Encontrados {len(selects_cercanos)} selects cerca de '{texto}'")
                        return self._procesar_selects_cercanos(selects_cercanos)
                        
                except:
                    continue
            
            print("❌ No se encontraron filtros por texto")
            return False
            
        except Exception as e:
            print(f"❌ Error en búsqueda avanzada: {e}")
            return False

    def _procesar_selects_cercanos(self, selects):
        """Procesar los selects encontrados cerca de los textos de filtro"""
        try:
            if len(selects) >= 2:
                print("🎯 Procesando selects encontrados...")
                
                # Primer select - intentar Nacional (Bolivia)
                select1 = Select(selects[0])
                opciones1 = [option.text for option in select1.options]
                print(f"📋 Opciones primer select: {opciones1}")
                
                for opcion in opciones1:
                    if "Nacional" in opcion or "Bolivia" in opcion:
                        select1.select_by_visible_text(opcion)
                        print(f"✅ Seleccionado: {opcion}")
                        break
                else:
                    # Si no encuentra, seleccionar primera opción
                    select1.select_by_index(0)
                    print("✅ Seleccionada primera opción")
                
                time.sleep(2)
                
                # Segundo select - intentar Potosí
                select2 = Select(selects[1])
                opciones2 = [option.text for option in select2.options]
                print(f"📋 Opciones segundo select: {opciones2}")
                
                for opcion in opciones2:
                    if "Potosí" in opcion or "Potos" in opcion:
                        select2.select_by_visible_text(opcion)
                        print(f"✅ Seleccionado: {opcion}")
                        break
                else:
                    # Si no encuentra, seleccionar primera opción
                    select2.select_by_index(0)
                    print("✅ Seleccionada primera opción")
                
                time.sleep(5)
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Error procesando selects: {e}")
            return False

    def extraer_datos_de_tablas(self):
        """Extraer datos de todas las tablas en la página"""
        print("📊 Extrayendo datos de tablas HTML...")
        
        try:
            # Obtener el HTML de la página
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encontrar todas las tablas
            tablas = soup.find_all('table')
            print(f"🔍 Encontradas {len(tablas)} tablas en la página")
            
            datos_extraidos = {}
            
            for i, tabla in enumerate(tablas):
                print(f"\n📋 Procesando tabla {i+1}...")
                
                # Extraer datos de la tabla
                datos_tabla = self._procesar_tabla(tabla)
                if datos_tabla:
                    datos_extraidos[f'tabla_{i+1}'] = datos_tabla
                    print(f"✅ Tabla {i+1} procesada - {len(datos_tabla)} filas")
                else:
                    print(f"❌ Tabla {i+1} vacía o no procesable")
            
            return datos_extraidos
            
        except Exception as e:
            print(f"❌ Error extrayendo datos de tablas: {e}")
            return None
    
    def _procesar_tabla(self, tabla):
        """Procesar una tabla individual y extraer sus datos"""
        try:
            filas = tabla.find_all('tr')
            if len(filas) < 2:  # Menos de header + una fila de datos
                return None
            
            datos = []
            encabezados = []
            
            # Procesar encabezados (primera fila)
            celdas_encabezado = filas[0].find_all(['th', 'td'])
            encabezados = [celda.get_text(strip=True) for celda in celdas_encabezado]
            
            # Procesar filas de datos
            for fila in filas[1:]:
                celdas = fila.find_all('td')
                if celdas:
                    fila_datos = [celda.get_text(strip=True) for celda in celdas]
                    
                    # Crear diccionario si tenemos encabezados
                    if encabezados and len(encabezados) == len(fila_datos):
                        fila_dict = dict(zip(encabezados, fila_datos))
                        datos.append(fila_dict)
                    else:
                        datos.append(fila_datos)
            
            return datos
            
        except Exception as e:
            print(f"❌ Error procesando tabla: {e}")
            return None
    
    def close(self):
        """Cerrar el navegador"""
        if self.driver:
            print("🔒 Cerrando navegador...")
            self.driver.quit()

def main():
    print("🚀 MONITOREO OEP - CON FILTROS GEOGRÁFICOS")
    print("=" * 50)
    print("🎯 Objetivo: Nacional (Bolivia) → Potosí")
    print("=" * 50)
    
    # Credenciales
    usuario = "dante.ibanez"
    password = "Electoral2025"
    
    # Inicializar Selenium
    monitoreo = MonitoreoSelenium()
    
    try:
        # Configurar driver
        monitoreo.setup_driver()
        
        # Hacer login
        if monitoreo.login(usuario, password):
            print("\n" + "="*50)
            print("✅ LOGIN EXITOSO - APLICANDO FILTROS")
            print("="*50)
            
            # Estrategia 1: Aplicar filtros automáticamente
            print("\n🗺️ Aplicando filtros geográficos...")
            filtros_aplicados = monitoreo.aplicar_filtros_geograficos()
            
            if not filtros_aplicados:
                # Estrategia 2: Búsqueda avanzada de filtros
                print("\n🔍 Intentando búsqueda avanzada de filtros...")
                monitoreo.buscar_y_aplicar_filtros_avanzado()
            
            # Extraer datos después de aplicar filtros
            print("\n📊 Extrayendo datos con filtros aplicados...")
            datos_tablas = monitoreo.extraer_datos_de_tablas()
            
            if datos_tablas:
                print(f"✅ Se extrajeron datos de {len(datos_tablas)} tablas")
                
                # Guardar datos de tablas
                with open('monitoreo_CON_FILTROS.json', 'w', encoding='utf-8') as f:
                    json.dump(datos_tablas, f, indent=2, ensure_ascii=False, default=str)
                print("💾 Datos con filtros guardados en 'monitoreo_CON_FILTROS.json'")
                
                # Mostrar resumen de lo encontrado
                for tabla_nombre, datos in datos_tablas.items():
                    if datos and len(datos) > 0:
                        print(f"\n📋 {tabla_nombre.upper()}:")
                        if isinstance(datos[0], dict):
                            # Es una tabla con encabezados
                            claves = list(datos[0].keys())
                            print(f"   Columnas: {claves}")
                            print(f"   Filas: {len(datos)}")
                            # Mostrar primera fila completa
                            if datos[0]:
                                print(f"   Primera fila: {datos[0]}")
            
            # Guardar HTML final con filtros aplicados
            html_final = monitoreo.driver.page_source
            with open('monitoreo_con_filtros.html', 'w', encoding='utf-8') as f:
                f.write(html_final)
            print("💾 HTML con filtros guardado en 'monitoreo_con_filtros.html'")
            
            # Screenshot final
            monitoreo.driver.save_screenshot('monitoreo_final_con_filtros.png')
            print("📸 Screenshot final: 'monitoreo_final_con_filtros.png'")
            
            print("\n" + "="*50)
            print("🎉 PROCESO COMPLETADO!")
            print("="*50)
            print("📁 ARCHIVOS GENERADOS:")
            print("   - monitoreo_CON_FILTROS.json (datos con filtros aplicados)")
            print("   - monitoreo_con_filtros.html (HTML con filtros)")
            print("   - monitoreo_final_con_filtros.png (screenshot final)")
            print("   - antes_filtros.png, despues_filtros.png (comparación)")
            
        else:
            print("❌ No se pudo hacer login")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Esperar antes de cerrar
        input("\nPresiona Enter para cerrar el navegador...")
        monitoreo.close()

if __name__ == "__main__":
    main()