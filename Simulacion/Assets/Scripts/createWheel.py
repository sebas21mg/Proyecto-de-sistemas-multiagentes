# Autor: Sebastian Moncada - A01027028

# Programa para crear el modelo de una rueda teniendo como parámetros el número
# de lados, el radio y el ancho

import math
import os

carpetaActual = os.path.dirname(__file__)
rutaObjeto = os.path.join(carpetaActual, '../Models/wheel.obj')
archivo = open(rutaObjeto, "w")

# Parámetros del programa
numLados = 8
radio = 0.06
anchoIn = 0.07


def createVertices():  # Calcular los vertices
    # Hacer ambas caras de la rueda (por eso el rango es 2)
    for i in range(2):
        # La primera cara se genera en el eje x positivo y la segunda en el negativo
        if i == 1:
            ancho = round(-anchoIn / 2, 4)
        else:
            ancho = round(anchoIn / 2, 4)

        vertices.append([ancho, 0, 0])  # Origen de la cara (0,0)

        # Calcular los vértices del círculo de cada cara teniendo en cuenta cuántos lados se requieren
        for j in range(numLados):
            angle = math.radians(360 / numLados * (j + 1))
            y = round(radio * math.sin(angle), 4)
            z = round(radio * math.cos(angle), 4)

            vertices.append([ancho,  y,  z])


# Calcular el vector normal entre tres vértices usando los índices que tienen estos en el vector de vertices
def calculateNormalVector(i1, i2, i3):
    u = [vertices[i2][0] - vertices[i1][0],
         vertices[i2][1] - vertices[i1][1],
         vertices[i2][2] - vertices[i1][2]]

    v = [vertices[i3][0] - vertices[i1][0],
         vertices[i3][1] - vertices[i1][1],
         vertices[i3][2] - vertices[i1][2]]

    w = [u[1] * v[2] - u[2] * v[1],
         u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0]]

    return [w[0], w[1], w[2]]


def normalizeVector(vector):
    # Calcular la magnitud del vector
    magnitude = math.sqrt(sum(element**2 for element in vector))

    # Normalizar cada elemento dividiéndola por la magnitud
    normalizedVector = [element / magnitude for element in vector]

    # Redondear los elementos del vector a 4 decimales
    return [round(normalizedVector[0], 4), round(normalizedVector[1], 4), round(normalizedVector[2], 4)]


def verticesPattern():  # Crear las caras y los vectores normales usando el patrón pertinente de las vértices en el vector de vértices
    for i in range(numLados):
        if (i < numLados - 1):
            useVerticesPattern(0, i + 2, i + 1)
            useVerticesPattern(numLados + 1, numLados +
                               2 + i, numLados + 3 + i)
            useVerticesPattern(1 + i, 2 + i, numLados + 2 + i)
            useVerticesPattern(2 + i, numLados + 3 + i, numLados + 2 + i)
        else:
            useVerticesPattern(0, 1, 1 + i)
            useVerticesPattern(numLados + 1, numLados + 2 + i, numLados + 2)
            useVerticesPattern(1 + i, 1, numLados + 2 + i)
            useVerticesPattern(1, numLados + 2, numLados + 2 + i)


# Crear la cara y el vector normal del los vértices dados
def useVerticesPattern(x, y, z):
    createFace(x + 1, y + 1, z + 1)
    createNormal(x, y, z)


def createFace(x, y, z):  # Calcular la cara
    faces.append([x, y, z])


def createNormal(x, y, z):  # Obtener el vector normal
    normals.append(normalizeVector(calculateNormalVector(x, y, z)))


# Vectores para almacenar los datos que se van a enviar al obj
vertices = []
normals = []
faces = []
createVertices()
verticesPattern()

# Agregar los vertices, normals y faces al output
output = ["# Vertices:\n\n"]
for vertice in vertices:
    output.append("v " +
                  str(vertice[0]) + " " +
                  str(vertice[1]) + " " +
                  str(vertice[2]) + "\n")

output.append("\n# Normals:\n\n")
for normal in normals:
    output.append("vn " +
                  str(normal[0]) + " " +
                  str(normal[1]) + " " +
                  str(normal[2]) + "\n")

output.append("\n# Faces:\n\n")
for i in range(len(faces)):
    output.append("f " +
                  str(faces[i][0]) + "//" + str(i + 1) + " " +
                  str(faces[i][1]) + "//" + str(i + 1) + " " +
                  str(faces[i][2]) + "//" + str(i + 1) + "\n")

# Escribir todo el output en el archivo abierto
archivo.writelines(output)
archivo.close()
