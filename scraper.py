import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import json

def configurar_driver():
    """Configura Chrome para funcionar tanto en local como en GitHub Actions"""
    opciones = uc.ChromeOptions()
    opciones.add_argument('--headless=new')  # Ejecutar sin interfaz gráfica
    opciones.add_argument('--no-sandbox')    # Necesario en contenedores
    opciones.add_argument('--disable-dev-shm-usage')  # Evitar problemas de memoria compartida
    opciones.add_argument('--disable-gpu')   # Deshabilitar GPU en entornos sin aceleración
    opciones.add_argument('--remote-debugging-port=0')  # Puerto de depuración automático
    opciones.add_argument('--window-size=1920,1080')  # Tamaño de ventana
    
    driver = uc.Chrome(options=opciones)
    return driver

def obtener_cuotas_betplay():
    driver = configurar_driver()
    try:
        driver.get('https://www.betplay.com.co/deportes/futbol')
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Aquí debes inspeccionar la página web (F12) y buscar las clases CSS de las cuotas.
        # Ejemplo: cuotas = soup.find_all('span', class_='bet-odds')
        # Por ahora, simulamos datos de prueba
        cuotas = [{'equipo': 'Junior', 'cuota': 2.10, 'casa': 'BetPlay'},
                  {'equipo': 'Millonarios', 'cuota': 1.85, 'casa': 'BetPlay'}]
        return cuotas
    finally:
        driver.quit()

def obtener_cuotas_wplay():
    driver = configurar_driver()
    try:
        driver.get('https://www.wplay.co/deportes/futbol')
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cuotas = [{'equipo': 'Junior', 'cuota': 2.05, 'casa': 'WPlay'},
                  {'equipo': 'Millonarios', 'cuota': 1.90, 'casa': 'WPlay'}]
        return cuotas
    finally:
        driver.quit()

def comparar_cuotas(betplay, wplay):
    oportunidades = []
    for bp in betplay:
        for wp in wplay:
            if bp['equipo'] == wp['equipo']:
                # Fórmula correcta de arbitraje:
                # Si (1 - (1/cuota1 + 1/cuota2)) * 100 > 0, hay oportunidad de arbitraje
                suma_inversos = 1/bp['cuota'] + 1/wp['cuota']
                ganancia_porcentual = round((1 - suma_inversos) * 100, 2)
                
                # Solo guardamos si realmente hay oportunidad de arbitraje (ganancia positiva)
                if ganancia_porcentual > 0:
                    # Solo si BetPlay tiene mejor cuota (como solicitaste originalmente)
                    if bp['cuota'] > wp['cuota']:
                        oportunidades.append({
                            'partido': bp['equipo'],
                            'apuesta_en_betplay': bp['cuota'],
                            'apuesta_en_wplay': wp['cuota'],
                            'ganancia_porcentual': ganancia_porcentual,
                            'suma_inversos': round(suma_inversos, 4)  # Para verificar el cálculo
                        })
    return oportunidades

if __name__ == "__main__":
    print("Escaneando BetPlay...")
    bp = obtener_cuotas_betplay()
    print("Escaneando WPlay...")
    wp = obtener_cuotas_wplay()
    
    print("\nComparando cuotas para encontrar oportunidades de arbitraje...")
    ops = comparar_cuotas(bp, wp)
    
    with open('oportunidades.json', 'w', encoding='utf-8') as f:
        json.dump(ops, f, ensure_ascii=False, indent=2)
    
    print(f"Se encontraron {len(ops)} oportunidades. Guardadas en oportunidades.json")
    
    # Mostrar resultados en consola
    if ops:
        print("\nOportunidades encontradas:")
        for op in ops:
            print(f"- {op['partido']}: BetPlay {op['apuesta_en_betplay']} vs WPlay {op['apuesta_en_wplay']} = {op['ganancia_porcentual']}% ganancia")
    else:
        print("No se encontraron oportunidades de arbitraje en este momento.")
