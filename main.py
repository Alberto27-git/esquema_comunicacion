"""
Esquema de comunicación de Shannon - Teoría de la información
Alberto Ortíz López
"""
#librerias necesarias
import requests
from bs4 import BeautifulSoup
import time
from random import randint, random

megabit_bytes = 125000

class Canal:
    def __init__(self, data, ruido_EM, prob_perdida, velocidad):
        self.data = data
        self.ruido_EM = ruido_EM
        self.prob_perdida = prob_perdida
        self.velocidad = velocidad
    
    def envia_receptor(self, paquete):
        print("Recibiendo...")
        #Probabilidad de corromper los datos por ruido electromagnético
        if self.ruido_EM:
            num_rand_prob = randint(0, len(self.prob_perdida)-1 )
            if self.prob_perdida[num_rand_prob] % 2 == 0:
                paquete.header = False
        
        #Envia el paquete con o sin ruido dependiendo de la probabilidad anterior
        receptor_1.decodifica_paquete(paquete)
        print("STORAGE: ", len(receptor_1.storage))
        time.sleep(1)

class Paquete:
    def __init__(self, header, data,  tail):
        self.header = header
        self.data = data
        self.tail = tail

class Receptor:
    def __init__(self, storage):
        self.storage = storage
    
    def decodifica_paquete(self, paquete):
        if paquete.header and paquete.tail:
            caracteres = [chr(int(byte, 2)) for byte in paquete.data]
            receptor_1.storage += ''.join(caracteres)

def crea_canal():
    prob_perdida = [2,4,5,7,8]

    vel_actual = 10 - randint(4,9)
    vel_actual *= megabit_bytes

    prob_em = randint(1,10)
    if prob_em % 2 == 0:
        return Canal(0, True, prob_perdida, vel_actual)
    else:
        return Canal(0, False, prob_perdida, vel_actual)

def Fuente_informacion(website):
    try:
        response = requests.get(website)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa
        return response.text        
    
    except Exception as e:
        #Enviar excepción por el Transmisor
        error = f'Error: {e}'
        return error
    
def Transmisor(contenido):
    contenido_bin =  ' '.join(format(ord(caracter), '08b') for caracter in contenido)
    bin_paquetes = [byte for byte in contenido_bin.split(' ')]
    
    while bin_paquetes:
        segmento = Paquete(True,bin_paquetes[:canal_1.velocidad],True)
        del bin_paquetes[:canal_1.velocidad]
        #Empezar a transmitir por el canal en paquetes segun la velocidad
        canal_1.envia_receptor(segmento)

def Destino(html):
    soup = BeautifulSoup(html, 'lxml')
    print(soup.prettify())

canal_1 = crea_canal()
receptor_1 = Receptor('')

def main():
    #website = "https://es.wikipedia.org/wiki/Enciclopedia" # 183,511
    #website = "https://es.wikipedia.org/wiki/Democracia" # 316,491
    website = "https://es.wikipedia.org/wiki/Wikipedia" # 648,469
    #https://www.microsoft.com/es-mx/

    #website = input("Ingresa url: ")

    print("Buscando en la web...\n")
    #Web scraping de la URL del usuario
    contenido = Fuente_informacion(website)

    print("Iniciando descarga...\n")
    Transmisor(contenido)
    Destino(receptor_1.storage)

main()