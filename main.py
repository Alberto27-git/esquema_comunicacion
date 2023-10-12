"""
Esquema de comunicación de Shannon - Teoría de la información
Alberto Ortíz López
"""
#librerias necesarias
import requests
from bs4 import BeautifulSoup
import time
import math
from random import randint, shuffle
import heapq

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
    def __init__(self, storage, metodo):
        self.storage = storage
        self.metodo = metodo
    
    def recibe_paquete(self, paquete):
        self.storage = self.metodo.decodifica(paquete, self.metodo.arbol)
        #print("SIUUUU", type(self.metodo.arbol))
        #self.storage += self.metodo.decodifica(paquete.data)

        #caracteres = [chr(int(byte, 2)) for byte in paquete.data]
        #self.storage += ''.join(caracteres)
        
        print("Bytes recibidos (acumulados) ", len(self.storage))

class Transmisor:
    def __init__(self, contenido, metodo):
        self.contenido = contenido
        self.metodo = metodo

    def transmite(self, receptor, canal, entropia):
        print(f"Codificación {self.metodo.nombre}")
        
        bin_caracteres = self.metodo.texto_a_binario(self.contenido)
        
        if self.metodo.nombre != "Binaria":
            codificado, self.metodo.arbol = self.metodo.codifica(bin_caracteres)
            print("TEXTO CODIFICADO\n",codificado)
            
            texto_original = self.metodo.decodifica(codificado, self.metodo.arbol)
            print("TEXTO ORIGINAL", texto_original)

        ruido = Ruido(8,20,self.metodo.ruido)
        id_paquete = 0

        while bin_caracteres:
            paquete = Paquete(id_paquete, bin_caracteres[:canal.velocidad],id_paquete)
            del bin_caracteres[:canal.velocidad]
            #Empezar a transmitir por el canal en paquetes segun la velocidad
            #la velocidad es la cantidad de bytes que se envian en un segundo en este caso
            #125000 bytes que son 1 megabits
           
            canal.envia_receptor(receptor, paquete, entropia, ruido)
            id_paquete += 1

class metodo_codificacion():
    def __init__(self, nombre, ruido):
        self.nombre = nombre
        self.ruido = ruido

    def contar_frecuencia(self, paquete_bytes):
        frecuencia = {}
        for simbolo in paquete_bytes:
            if simbolo in frecuencia:
                frecuencia[simbolo] += 1
            else:
                frecuencia[simbolo] = 1

        return frecuencia
    
    def texto_a_binario(self, texto):
        contenido_bin =  ' '.join(format(ord(caracter), '08b') for caracter in texto)
        return [byte for byte in contenido_bin.split(' ')]

class Binaria_normal(metodo_codificacion):
    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)

class Nodo_huffman():
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.izq = None
        self.der = None

    def __lt__(self, other):
        return self.freq < other.freq

class Huffman(metodo_codificacion):

    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)
        self.arbol = None

    def codifica(self, paquete_bytes):
        frecuencias = self.contar_frecuencia(paquete_bytes)
        arbol = self.construir_arbol(frecuencias)
        codificacion = self.codificar_arbol(arbol)
        return "".join([codificacion[char] for char in paquete_bytes]), arbol
        
    def construir_arbol(self,frecuencias):
        cola_prioridad = [Nodo_huffman(char, freq) for char, freq in frecuencias.items()]
        heapq.heapify(cola_prioridad)

        while len(cola_prioridad) > 1:
            izq = heapq.heappop(cola_prioridad)
            der = heapq.heappop(cola_prioridad)

            nodo_combinado = Nodo_huffman(None, izq.freq + der.freq)
            nodo_combinado.izq = izq
            nodo_combinado.der = der

            heapq.heappush(cola_prioridad, nodo_combinado)

        return cola_prioridad[0]

    def codificar_arbol(self, nodo, codigo_binario="", mapping=None):
        if mapping is None:
            mapping = {}

        if nodo is not None:
            if nodo.char is not None:  # Si es una hoja
                mapping[nodo.char] = codigo_binario
            self.codificar_arbol(nodo.izq, codigo_binario + "0", mapping)
            self.codificar_arbol(nodo.der, codigo_binario + "1", mapping)

        return mapping
    
    def decodifica(self,texto_codificado, arbol):
        #Decodificación de Huffman (comprimido) a binario
        nodo_actual = arbol
        texto_original = ""
        for bit in texto_codificado:
            if bit == "0":
                nodo_actual = nodo_actual.izq
            else:
                nodo_actual = nodo_actual.der

            if nodo_actual.char:
                texto_original += nodo_actual.char
                nodo_actual = arbol

        #Decodificación a ASCII
        lista_bytes = [texto_original[i:i+8] for i in range(0, len(texto_original), 8)]
        caracteres = [chr(int(byte, 2)) for byte in lista_bytes]
        
        return ''.join(caracteres)

class Shannon_fano(metodo_codificacion):

    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)
        self.arbol = None

    def codifica(self, contenido):
        print("Construyendo codificación")

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
    def __init__(self, velocidad):
        self.velocidad = velocidad
    
    def envia_receptor(self, receptor, paquete, entropia, ruido):
        entropia.total_paquetes_enviados += 1
        print("Recibiendo...")
        #Si se aplica ruido dependiendo de la codificación
        if ruido.aplicar:
            #Probabilidad de perder un paquete por ruido electromagnético
            if ruido.prob_afectar_datos():
                paquete = ruido.genera_ruido(paquete)
                entropia.registro_ruido.append(True)
                
        #Envia el paquete con o sin ruido dependiendo
        #  de la probabilidad anterior y la codificación
        receptor.recibe_paquete(paquete)
        time.sleep(1)

class Ruido:
    def __init__(self, umbral, rango_max, aplicar):
        self.umbral = umbral
        self.rango_max = rango_max
        self.aplicar = aplicar
    
    def prob_afectar_datos(self):
        num_aleatorio = randint(1, self.rango_max)
        #Probabilidad del 40% de caer en el rango del umbral
        #Número del 1 al 8
        if num_aleatorio <= self.umbral:
            return True
        
    def genera_ruido(self,paquete):
        shuffle(paquete.data)
        return paquete

class Paquete:
    def __init__(self, header, data,  tail):
        self.header = header
        self.data = data
        self.tail = tail

class Destino:
    def __init__(self, html):
        self.html = html

    def muestra_transmision_recibida(self):
        soup = BeautifulSoup(self.html, "html.parser")
        print(soup.prettify())

def crea_canal():
    
    megabit_bytes = 10000 #125000 #Cuanto equivale un megabit en bytes
    vel_actual = 1
    vel_actual = round(vel_actual * megabit_bytes)    
    return Canal(vel_actual)

def main():
    #URLS de prueba
    #website = "https://www.microsoft.com/es-mx/" #Pocos caracteres
    website = "https://octopus.mx" #un solo mensaje

    #website = "https://openai.com/" #102,487
    #website = "https://es.wikipedia.org/wiki/Wikipedia" # 650,693
    #website = "https://www.alamosinn.com/photo-albums" # 1,206,372
    
    #website = input("Ingresa url: ")

    #Web scraping de la URL del usuario
    print(f"Buscando en la web: {website} \n")
    fuente = Fuente_informacion(website)
    print("Iniciando descarga...\n")
    contenido = fuente.descarga_info()
    
    #Creo el objeto entropia para guardar un registro en el canal
    entropia = Entropia(0, 0, [])
    
    print("Contenctando...")
    canal = crea_canal()
    
    print("¿Que método de codificación usar?\
          \n1.-Binaria (normal)\n2.-Huffman\n3.-Shannon-Fano")
    
    while(True):
        tipo_codi = int(input())
        match tipo_codi:
            case 1:
                
                #transmisor = Transmisor(contenido, Binaria_normal("Binaria", True)  )
                #receptor = Receptor('', transmisor.metodo)
                return print("MÉTODO FUERA DE USO")
                
            case 2:
                transmisor = Transmisor(contenido, Huffman("Huffman", False))
                receptor = Receptor('', transmisor.metodo)
                break
            case 3:
                transmisor = Transmisor(contenido, Shannon_fano("Shannon Fano", False))
                receptor = Receptor('', transmisor.metodo)
                break
            case _:
                print("Opción no válida. Elige otra: ")
    
    transmisor.transmite(receptor, canal, entropia)
    #Finalmente muestro al usuario el resultado
    #Descargar HTML y comparar lo que pesaria completo con lo que pesó finalmente
    destino = Destino(receptor.storage)
    #destino.muestra_transmision_recibida()

    #entropia.calcula_entropia()
main()
