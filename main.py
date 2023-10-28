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
        #print(self.metodo.nombre, paquete.data )
        self.storage += paquete.data
        print("Bytes recibidos (acumulados) ", len(self.storage))
    
    def decodificacion(self):
        return self.metodo.decodifica("".join(self.storage), self.metodo.arbol)

class Transmisor:
    def __init__(self, contenido, metodo):
        self.contenido = contenido
        self.metodo = metodo

    def transmite(self, receptor, canal, entropia):
        print(f"-- Codificación {self.metodo.nombre} --")
        time.sleep(1)
        
        #Se convierte el html descargado a binario
        bin_caracteres = self.metodo.texto_a_binario(self.contenido)

        #El método de clase 'genera_codigos' regresa el código generado 
        # y el árbol para descomprimir el mismo.
        codigo = self.metodo.genera_codigos(bin_caracteres)

        #Regresa el código del método usado en una cadena de texto
        if self.metodo.nombre != "RLE" and self.metodo.nombre != "Combinatoria Binaria":
            codigo = self.metodo.construye_codigo(codigo, bin_caracteres)

        #Para poder enviarlo por paquetes es necesario convertir el código generado en una lista
        codigo = self.metodo.cadena_str_list(codigo)
                
        ruido = Ruido(8,20,self.metodo.ruido)
        id_paquete = 0

        while codigo:
            paquete = Paquete(id_paquete, codigo[:canal.velocidad],id_paquete)
            del codigo[:canal.velocidad]

            #Empezar a transmitir por el canal por paquetes segun la velocidad
            #la velocidad es la cantidad de bytes que se envian            
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
    
    def binario_a_texto(self, texto):
        return ''.join([ chr(int(byte, 2)) for byte in self.cadena_str_list(texto) ])

    def cadena_str_list(self, cadena_bin):
        return [cadena_bin[i:i+8] for i in range(0, len(cadena_bin), 8)]
    
    def construye_codigo(self, codificacion, lista_bytes):
       return "".join([codificacion[char] for char in lista_bytes])

class Combinatoria_binaria(metodo_codificacion):
    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)
        self.arbol = {
            "00": '1',
            "01": '2',
            "10": '3',
            "11": '4',
            "1": '5',
            "0": '6'
        }

    def genera_codigos(self, msg):
        msg = ''.join(msg)
        codigo = []
        for i in range(0, len(msg), 2):
            par = msg[i:i+2]
            codigo.append(self.arbol[par])

        return ''.join(codigo)

    def decodifica(self, codigo, arbol):
        decodificado = ''

        diccionario_invertido = {v: k for k, v in arbol.items()}
        
        for i in codigo:
            decodificado += diccionario_invertido[i]

        return self.binario_a_texto(decodificado)

class RLE(metodo_codificacion):
    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)
        self.arbol = None
    
    def genera_codigos(self, message):
        message = ''.join(message)
        
        encoded_message = ''
        i = 0

        while (i <= len(message)-1):
            count = 1
            ch = message[i]
            j = i
            while (j < len(message)-1):
                if (message[j] == message[j+1]):
                    count = count+1
                    j = j+1
                else:
                    break
            encoded_message = encoded_message+str(count)+ch
            i = j+1
        #print(encoded_message)
        return encoded_message

    def decodifica(self, encoded_msg, arbol):
        texto_descomprimido = ""

        for i in range(0, len(encoded_msg), 2):
            if i + 1 < len(encoded_msg):
                count = int(encoded_msg[i])

                texto_descomprimido += encoded_msg[i+1] * count

        return self.binario_a_texto(texto_descomprimido)

class Huffman(metodo_codificacion):

    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)
        self.arbol = None

    def genera_codigos(self, paquete_bytes):
        frecuencias = self.contar_frecuencia(paquete_bytes)
        self.arbol = self.construir_arbol(frecuencias)
        codificacion = self.codificar_arbol(self.arbol)
        return codificacion
        
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
    
    def decodifica(self, texto_codificado, arbol):
        #Decodificación de Huffman (comprimido) a binario
        nodo_actual = arbol
        binario = ""
        for bit in texto_codificado:
            if bit == "0":
                nodo_actual = nodo_actual.izq
            else:
                nodo_actual = nodo_actual.der

            if nodo_actual.char:
                binario += nodo_actual.char
                nodo_actual = arbol

        #Decodificación a ASCII
        texto = self.binario_a_texto(binario)
        return texto

class Nodo_huffman():
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.izq = None
        self.der = None

    def __lt__(self, other):
        return self.freq < other.freq

class Shannon_fano(metodo_codificacion):

    def __init__(self, nombre, ruido):
        super().__init__(nombre, ruido)
        self.arbol = None

    def genera_codigos(self, paquete_bytes):
        if len(paquete_bytes) == 1:
            return {paquete_bytes[0]: "0"}

        frecuencias = self.contar_frecuencia(paquete_bytes)
        frecuencias_ordenadas = sorted(frecuencias.items(), key=lambda x: x[1], reverse=True)

        # Dividir los caracteres en dos grupos aproximadamente iguales
        medio = len(frecuencias_ordenadas) // 2
        grupo1 = frecuencias_ordenadas[:medio]
        grupo2 = frecuencias_ordenadas[medio:]

        # Recursivamente asignar '0' a los caracteres en el primer grupo y '1' al segundo grupo
        codigo_grupo1 = self.genera_codigos([item[0] for item in grupo1])
        codigo_grupo2 = self.genera_codigos([item[0] for item in grupo2])

        # Combinar los códigos de ambos grupos
        codigo_final = {}
        for caracter, codigo in codigo_grupo1.items():
            codigo_final[caracter] = '0' + codigo
        for caracter, codigo in codigo_grupo2.items():
            codigo_final[caracter] = '1' + codigo
        
        self.arbol = codigo_final
        return codigo_final
    
    def decodifica(self, codigo, codigo_shannon_fano):
        binario = ""
        # Invertir el diccionario de códigos
        codigo_inverso = {v: k for k, v in codigo_shannon_fano.items()}  

        codigo_actual = ""
        for bit in codigo:
            codigo_actual += bit
            if codigo_actual in codigo_inverso:
                caracter = codigo_inverso[codigo_actual]
                binario += caracter
                codigo_actual = ""
        
        texto = self.binario_a_texto(binario)
        return texto


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
    
    megabit_bytes = 8000 #125000 #Cuanto equivale un megabit en bytes
    vel_actual = 1
    vel_actual = round(vel_actual * megabit_bytes)
    return Canal(vel_actual)

def main():
    #URLS de prueba
    #website = "https://www.microsoft.com/es-mx/" #Pesa poco
    
    #website = "https://es.wikipedia.org/wiki/Wikipedia:Portada" #Peso medio
    #website = "https://www.alamosinn.com/photo-albums" #Pesa mucho
    
    website = input("Ingresa url: ")

    #Web scraping de la URL del usuario
    print(f"Buscando en la web... {website}    \n")
    fuente = Fuente_informacion(website)

    print("Iniciando descarga...\n")
    contenido = fuente.descarga_info()
    #Creo el objeto entropia para guardar un registro en el canal
    entropia = Entropia(0, 0, [])
    
    print("Contenctando...")
    time.sleep(1)
    canal = crea_canal()

    siruido = input("¿Quieres aplicar probabilidad de ruido? (True/False): ")
    if siruido == "False":
        siruido = False
    else: siruido = True

    print("¿Que método de codificación usar?\
          \n1.-Shannon fano\n2.-Huffman\n3.-RLE (Más Lento)\n4.-Combinatoria Binaria")

    while(True):
        tipo_codi = int(input())
        match tipo_codi:
            case 1:
                transmisor = Transmisor(contenido, Shannon_fano("Shannon Fano", siruido))
                receptor = Receptor([], transmisor.metodo)
                break
            case 2:
                transmisor = Transmisor(contenido, Huffman("Huffman", siruido))
                receptor = Receptor([], transmisor.metodo)
                break
            case 3:
                transmisor = Transmisor(contenido, RLE("RLE", siruido)  )
                receptor = Receptor([], transmisor.metodo)
                break
            case 4:
                transmisor = Transmisor(contenido, Combinatoria_binaria("Combinatoria Binaria", siruido)  )
                receptor = Receptor([], transmisor.metodo)
                break
            case _:
                print("Opción no válida. Elige otra: ")
    
    transmisor.transmite(receptor, canal, entropia)

    recibido = receptor.decodificacion()
    #Finalmente muestro al usuario el resultado
    destino = Destino(recibido)
    destino.muestra_transmision_recibida()
    entropia.calcula_entropia()
main()
