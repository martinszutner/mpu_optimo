import subprocess
import sys

def ping_test(size, host, debug=False):
    """Envía un ping con un tamaño específico de paquete y devuelve True si no se necesita fragmentación."""
    try:
        # Ejecuta el comando ping con el tamaño especificado y el parámetro -f para no permitir fragmentación
        output = subprocess.check_output(
            ["ping", "-f", "-l", str(size), "-n", "1", host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        # Verifica si la salida contiene un mensaje indicando que se necesita fragmentación
        if "Fragmentation needed" in output or "Packet needs to be fragmented" in output:
            if debug:
                print(f"Size {size} bytes: Necesita fragmentación para {host}")
            return False
        else:
            if debug:
                print(f"Size {size} bytes: No necesita fragmentación para {host}")
            return True
    except subprocess.CalledProcessError as e:
        if debug:
            print(f"Size {size} bytes: Fallo del comando para {host} con error {e.output}")
        return False

def find_optimal_mtu(host, debug=False):
    """Encuentra el MTU óptimo mediante búsqueda binaria."""
    min_size = 0
    max_size = 1500
    optimal_size = 0

    # Búsqueda binaria para encontrar el tamaño máximo sin fragmentación
    while min_size <= max_size:
        mid_size = (min_size + max_size) // 2
        if ping_test(mid_size, host, debug):
            optimal_size = mid_size
            min_size = mid_size + 1
        else:
            max_size = mid_size - 1

    return optimal_size + 28  # Incluye 28 bytes de cabecera

def test_multiple_hosts(hosts, debug=False):
    """Prueba el MTU para una lista de hosts y devuelve el MTU óptimo para cada uno."""
    results = {}
    for host in hosts:
        if debug:
            print(f"\nProbando MTU para {host}")
        optimal_mtu = find_optimal_mtu(host, debug)
        results[host] = optimal_mtu
        if debug:
            print(f"MTU óptimo para {host}: {optimal_mtu} bytes")
    return results

def calculate_final_mtu(results):
    """Calcula el MTU final basado en diferentes estrategias."""
    mtu_values = list(results.values())
    min_mtu = min(mtu_values)
    max_mtu = max(mtu_values)
    average_mtu = sum(mtu_values) / len(mtu_values)

    # Imprime un análisis si hay más de un valor
    if len(mtu_values) > 1:
        print("\nAnálisis de MTU:")
        print(f"MTU Mínimo: {min_mtu} bytes")
        print(f"MTU Máximo: {max_mtu} bytes")
        print(f"MTU Promedio: {average_mtu:.2f} bytes")

    # Elige el valor mínimo para asegurar que funcione en todos los casos
    final_mtu = min_mtu
    return final_mtu

if __name__ == "__main__":
    # Comprueba si el parámetro -d está presente en los argumentos
    debug_mode = "-d" in sys.argv
    hosts = [
        "www.google.com",
        "www.facebook.com",
        "www.amazon.com",
        "www.cloudflare.com",
        "www.lanacion.com.ar",   # Diario La Nación
        "www.clarin.com",        # Diario Clarín
        "www.mercadolibre.com.ar", # Mercado Libre Argentina
        "www.infobae.com",       # Infobae
        "www.tn.com.ar"          # TN Todo Noticias
    ]
    
    # Prueba el MTU para los hosts especificados
    mtu_results = test_multiple_hosts(hosts, debug=debug_mode)
    # Calcula el MTU final basado en los resultados
    final_mtu = calculate_final_mtu(mtu_results)

    # Muestra el resultado final en función del modo de depuración
    if debug_mode:
        print(f"\nConfiguración final de MTU: {final_mtu} bytes")
    else:
        print(f"MTU óptimo: {final_mtu} bytes")
