"""
Esquema de comunicación de Shannon - Teoría de la información
Alberto Ortíz López
"""
#librerias necesarias
import requests
from bs4 import BeautifulSoup
import time
import math
from random import randint, random

umbral = 8
rango_max = 20

class Fuente_informacion:
    def __init__(self, website):
        self.website = website
    
    def descarga_info(self):
        try:
            response = requests.get(self.website)
            response.raise_for_status()  # Verificar si la solicitud fue exitosa
            return response.text        
    
        except Exception as e:
            #Enviar excepción por el Transmisor
            error = f'Error: {e}'
            return error

class Receptor:
    def __init__(self, storage):
        self.storage = storage
    
    def decodifica_paquete(self, paquete):
        if paquete.header and paquete.tail:
            caracteres = [chr(int(byte, 2)) for byte in paquete.data]
            self.storage += ''.join(caracteres)

class Transmisor:
    def __init__(self, contenido):
        self.contenido = contenido

    def transmite(self, receptor, canal, entropia):
        contenido_bin =  ' '.join(format(ord(caracter), '08b') for caracter in self.contenido)
        bin_paquetes = [byte for byte in contenido_bin.split(' ')]
        
        while bin_paquetes:
            segmento = Paquete(True,bin_paquetes[:canal.velocidad],True)
            del bin_paquetes[:canal.velocidad]
            #Empezar a transmitir por el canal en paquetes segun la velocidad
            #la velocidad es la cantidad de bytes que se envian en un segundo en este caso
            #125000 bytes que son 1 megabits
            canal.envia_receptor(receptor, entropia, segmento)

class Entropia:
    def __init__(self, total_paquetes_enviados, entropia_final, registro_ruido):
        self.total_paquetes_enviados = total_paquetes_enviados
        self.entropia_final = entropia_final
        self.registro_ruido = registro_ruido
    
    def calcula_entropia(self):
        print(self.total_paquetes_enviados, "Probabilidad de pérdida")
        for i in range(0,len(self.registro_ruido)):
            self.entropia_final += (1/self.total_paquetes_enviados) * math.log2(1/self.total_paquetes_enviados)
            
        print("Entropia:", -self.entropia_final, )
        print("Veces que ocurrió ruido: ", len(self.registro_ruido))
        #calcular con las veces que se enviaron paquetes 
        # y la cantidad de veces que cayó ruido

class Canal:
    def __init__(self, data, velocidad):
        
        self.data = data
        self.velocidad = velocidad
    
    def envia_receptor(self, receptor, entropia, paquete):
        entropia.total_paquetes_enviados += 1
        print("Recibiendo...")
        #Probabilidad de perder un paquete por ruido electromagnético
        if self.ruido():
            entropia.registro_ruido.append(True)
            paquete.header = False
    
        #Envia el paquete con o sin ruido dependiendo de la probabilidad anterior
        receptor.decodifica_paquete(paquete)
        print("Tamaño de paquete recibido: ", len(receptor.storage))
        time.sleep(1)
    
    def ruido(self):
        num_aleatorio = randint(9,rango_max)
        #Probabilidad del 40% de caer en el rango del umbral
        #Número del 1 al 8
        if num_aleatorio <= umbral:
            return True

class Paquete:
    def __init__(self, header, data,  tail):
        self.header = header
        self.data = data
        self.tail = tail

class Destino:
    def __init__(self, html):
        self.html = html

    def muestra_transmision(self):
        soup = BeautifulSoup(self.html, 'lxml')
        print(soup.prettify())

def crea_canal():
    
    megabit_bytes = 125000 #Cuanto equivale un megabit en bytes
    vel_actual = 1
    vel_actual = int(vel_actual * megabit_bytes)    
    return Canal(None, vel_actual)

def main():
    #website = "https://www.alamosinn.com/" # 918,339
    #website = "https://www.alamosinn.com/explore" # 947,070
    #website = "https://www.alamosinn.com/photo-albums" # 1,204,958
    website = "https://www.frikidelto.com/tutorial/" # 1,204,998
    

    #website = input("Ingresa url: ")

    #Web scraping de la URL del usuario
    print(f"Buscando en la web: {website} \n")
    fuente = Fuente_informacion(website)
    contenido = fuente.descarga_info()

    #Creo el objeto entropia para guardar un registro en el canal
    entropia = Entropia(0, 0, [])
    
    canal = crea_canal()
    receptor = Receptor('')

    print("Iniciando descarga...\n")
    transmisor = Transmisor(contenido)
    transmisor.transmite(receptor, canal, entropia)

    #Finalmente muestro al usuario el resultado
    #Descargar HTML y comparar lo que pesaria completo con lo que pesó finalmente
    destino = Destino(receptor.storage)
    #destino.muestra_transmision()

    entropia.calcula_entropia()

main()