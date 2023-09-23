# Esquema de la comunicación
Un usuario desea recibir el código de HTML de cualquier página web y para eso debe ingresar una URL para que el servidor se lo regrese.

## Fuente de información:
El código HTML de una página web, la que el usuario desee. El usuario proporcion la URL.

## Transmisor:
La información se convierte a binario, se divide por bytes para que se puedan enviar en base a la velocidad del canal y se empaquetan con un "Header" y "Tail". Tanto "Header" como "Tail" seran valores booleanos True para indicar un empaquetado exitoso. 

## Canal:
El canal es un cable UTP de CAT3, con velocidad máxima de 1Mbps, que se ve interferida por la prescencia de ruido electromagnético (motor cercano), que provoca señal eléctrica diferente en la transmisión de datos y por lo tanto una distorsión en estos y que puede corromper el resultado final.

## Receptor: 
Desempaqueta los datos revisando su "Header" y "Tail", en caso de encontrar un empaquetado no deseado se descartará el paquete completo. Aquí se convierte de binario a caracteres ASCII, para posteriormente mandarlo al Destino.

## Destino: 
El código HTML descargado se muestra al usuario.




