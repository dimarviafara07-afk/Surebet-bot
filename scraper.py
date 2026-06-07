import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import json

def obtener_cuotas_betplay():
    driver = uc.Chrome()
    driver.get('https://www.betplay.com.co/deportes/futbol')  # URL real de fútbol en BetPlay
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Aquí debes inspeccionar la página web (F12) y buscar las clases CSS de las cuotas.
    # Ejemplo: cuotas = soup.find_all('span', class_='bet-odds')
    # Por ahora, simulamos datos de prueba
    cuotas = [{'equipo': 'Junior', 'cuota': 2.10, 'casa': 'BetPlay'},
              {'equipo': 'Millonarios', 'cuota': 1.85, 'casa': 'BetPlay'}]
    driver.quit()
    return cuotas

def obtener_cuotas_wplay():
    driver = uc.Chrome()
    driver.get('https://www.wplay.co/deportes/futbol')  # URL real
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cuotas = [{'equipo': 'Junior', 'cuota': 2.05, 'casa': 'WPlay'},
              {'equipo': 'Millonarios', 'cuota': 1.90, 'casa': 'WPlay'}]
    driver.quit()
    return cuotas

def comparar_cuotas(betplay, wplay):
    oportunidades = []
    for bp in betplay:
        for wp in wplay:
            if bp['equipo'] == wp['equipo']:
                # Si la cuota de BetPlay es mayor a la de WPlay, hay arbitraje
                if bp['cuota'] > wp['cuota']:
                    oportunidades.append({
                        'partido': bp['equipo'],
                        'apuesta_en_betplay': bp['cuota'],
                        'apuesta_en_wplay': wp['cuota'],
                        'ganancia_porcentual': round((1/bp['cuota'] + 1/wp['cuota']) * 100, 2)
                    })
    return oportunidades

if __name__ == "__main__":
    print("Escaneando BetPlay...")
    bp = obtener_cuotas_betplay()
    print("Escaneando WPlay...")
    wp = obtener_cuotas_wplay()
    ops = comparar_cuotas(bp, wp)
    with open('oportunidades.json', 'w') as f:
        json.dump(ops, f)
    print(f"Se encontraron {len(ops)} oportunidades. Guardadas en oportunidades.json")
