import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import json
import sys

def configurar_driver():
    """
    Configura Chrome para funcionar tanto en local como en GitHub Actions.
    Incluye todos los argumentos necesarios para entornos sin pantalla.
    """
    opciones = uc.ChromeOptions()
    
    # Argumentos esenciales para GitHub Actions y entornos headless
    opciones.add_argument('--headless=new')           # Modo sin interfaz gráfica (nuevo modo)
    opciones.add_argument('--no-sandbox')             # Obligatorio en contenedores Docker
    opciones.add_argument('--disable-dev-shm-usage')  # Evita errores de memoria /dev/shm
    opciones.add_argument('--disable-gpu')            # Deshabilita aceleración GPU
    opciones.add_argument('--remote-debugging-port=0') # Puerto de depuración automático
    opciones.add_argument('--disable-extensions')     # Deshabilita extensiones
    opciones.add_argument('--disable-setuid-sandbox') # Sandbox adicional deshabilitado
    opciones.add_argument('--window-size=1920,1080')  # Tamaño de ventana virtual
    
    # Opciones adicionales de estabilidad
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
    opciones.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = uc.Chrome(options=opciones)
        driver.set_page_load_timeout(30)  # Timeout de carga de página
        return driver
    except Exception as e:
        print(f"Error al crear el driver: {e}", file=sys.stderr)
        raise

def obtener_cuotas_betplay():
    """
    Obtiene las cuotas de BetPlay.
    Actualmente usa datos simulados - necesita implementar el scraping real.
    """
    driver = None
    try:
        print("Iniciando scraping de BetPlay...")
        driver = configurar_driver()
        driver.get('https://www.betplay.com.co/deportes/futbol')
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # TODO: Implementar scraping real de BetPlay
        # Necesitas inspeccionar la página y encontrar las clases CSS correctas
        # Ejemplo: 
        # cuotas = []
        # elementos = soup.find_all('div', class_='event-row')
        # for elem in elementos:
        #     equipo = elem.find('span', class_='team-name').text
        #     cuota = float(elem.find('span', class_='odd-value').text)
        #     cuotas.append({'equipo': equipo, 'cuota': cuota, 'casa': 'BetPlay'})
        
        # Datos de prueba (reemplazar con scraping real)
        cuotas = [
            {'equipo': 'Junior', 'cuota': 2.10, 'casa': 'BetPlay'},
            {'equipo': 'Millonarios', 'cuota': 1.85, 'casa': 'BetPlay'}
        ]
        
        print(f"BetPlay: {len(cuotas)} cuotas obtenidas")
        return cuotas
        
    except Exception as e:
        print(f"Error en BetPlay: {e}", file=sys.stderr)
        return []
    finally:
        if driver:
            driver.quit()

def obtener_cuotas_wplay():
    """
    Obtiene las cuotas de WPlay.
    Actualmente usa datos simulados - necesita implementar el scraping real.
    """
    driver = None
    try:
        print("Iniciando scraping de WPlay...")
        driver = configurar_driver()
        driver.get('https://www.wplay.co/deportes/futbol')
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # TODO: Implementar scraping real de WPlay
        # Necesitas inspeccionar la página y encontrar las clases CSS correctas
        
        # Datos de prueba (reemplazar con scraping real)
        cuotas = [
            {'equipo': 'Junior', 'cuota': 2.05, 'casa': 'WPlay'},
            {'equipo': 'Millonarios', 'cuota': 1.90, 'casa': 'WPlay'}
        ]
        
        print(f"WPlay: {len(cuotas)} cuotas obtenidas")
        return cuotas
        
    except Exception as e:
        print(f"Error en WPlay: {e}", file=sys.stderr)
        return []
    finally:
        if driver:
            driver.quit()

def comparar_cuotas(betplay, wplay):
    """
    Compara cuotas entre BetPlay y WPlay para encontrar oportunidades de arbitraje.
    Fórmula correcta: (1 - (1/cuota1 + 1/cuota2)) * 100
    Si el resultado es positivo, existe oportunidad de arbitraje.
    """
    oportunidades = []
    
    if not betplay or not wplay:
        print("No hay datos suficientes para comparar")
        return oportunidades
    
    print(f"Comparando {len(betplay)} cuotas de BetPlay con {len(wplay)} cuotas de WPlay...")
    
    for bp in betplay:
        for wp in wplay:
            if bp['equipo'] == wp['equipo']:
                # Cálculo correcto de arbitraje
                suma_inversos = 1/bp['cuota'] + 1/wp['cuota']
                ganancia_porcentual = round((1 - suma_inversos) * 100, 2)
                
                # Solo guardamos si hay oportunidad real de arbitraje (ganancia positiva)
                if ganancia_porcentual > 0:
                    # Verificamos si BetPlay tiene mejor cuota
                    if bp['cuota'] > wp['cuota']:
                        oportunidades.append({
                            'partido': bp['equipo'],
                            'apuesta_en_betplay': bp['cuota'],
                            'apuesta_en_wplay': wp['cuota'],
                            'ganancia_porcentual': ganancia_porcentual,
                            'suma_inversos': round(suma_inversos, 4),
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
    
    # Ordenar por mayor ganancia
    oportunidades.sort(key=lambda x: x['ganancia_porcentual'], reverse=True)
    return oportunidades

def guardar_resultados(oportunidades, archivo='oportunidades.json'):
    """Guarda los resultados en un archivo JSON"""
    resultado = {
        'fecha_escaneo': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_oportunidades': len(oportunidades),
        'oportunidades': oportunidades
    }
    
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"Resultados guardados en {archivo}")

def main():
    """Función principal"""
    print("=" * 60)
    print("ARBITRAJE DEPORTIVO - COMPARADOR DE CUOTAS")
    print("=" * 60)
    print(f"Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obtener cuotas de ambas casas
    print("Escaneando BetPlay...")
    bp = obtener_cuotas_betplay()
    
    print("\nEscaneando WPlay...")
    wp = obtener_cuotas_wplay()
    
    # Comparar cuotas
    print("\nAnalizando oportunidades de arbitraje...")
    ops = comparar_cuotas(bp, wp)
    
    # Guardar resultados
    guardar_resultados(ops)
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    
    if ops:
        print(f"\n✅ Se encontraron {len(ops)} oportunidades de arbitraje:\n")
        for i, op in enumerate(ops, 1):
            print(f"{i}. {op['partido']}")
            print(f"   BetPlay: {op['apuesta_en_betplay']} | WPlay: {op['apuesta_en_wplay']}")
            print(f"   Ganancia: {op['ganancia_porcentual']}%")
            print()
    else:
        print("\n❌ No se encontraron oportunidades de arbitraje en este momento.")
        print("   Esto es normal cuando las cuotas son muy similares entre casas.")
    
    print("=" * 60)
    print(f"Fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return len(ops)

if __name__ == "__main__":
    try:
        num_oportunidades = main()
        sys.exit(0 if num_oportunidades >= 0 else 1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}", file=sys.stderr)
        sys.exit(1)
