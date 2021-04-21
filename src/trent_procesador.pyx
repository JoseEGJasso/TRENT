# cython: language_level=3
import io
from PIL import Image
import numpy as np

cdef class PDI:
    ''' Clase que se encarga de la lógica de cada uno de los filtros y modificaciones'''

    cdef unsigned char[:, :, :] img_o  # Imagen original transformada a arreglo
    cdef unsigned char[:, :, :] img_m  # Imagen modificada
    cdef int ancho                     # Número de pixeles a lo ancho de la imagen original
    cdef int largo                     # Número de pixeles a lo largo de la imagen original
    cdef str img_formato               # Formato de la imagen original

    def __cinit__(self, ruta):
        ''' Carga la imagen en un arreglo de acuerdo a la ruta 

            ruta: str. Ruta de la imagen '''

        self.img_formato = Image.open(ruta).format 
        self.img_o = np.array(Image.open(ruta))            
        self.img_m = self.img_o.copy()             
        self.ancho = np.size(self.img_o,axis = 1)  
        self.largo = np.size(self.img_o,axis = 0)  


    def __modificar_rgb(self, int x, int y, rgb):
        '''Función que modifica los valores RGB del pixel en la posición (x,y) 
            x: int. Posición x del pixel
            y: int. Posición y del pixel
            rgb: list. Lista con los 3 nuevos valores del pixel'''

        cdef int z

        for z in range(0,3):
            self.img_m[x,y,z] = rgb[z]


    def __modificar_pixeles(self,ec):
        ''' Función que aplica la función recibida a los valores RGB del pixel y
            los nuevos valores generados por esta función se aplican al pixel

            ec. function. Función a aplicar'''

        cdef int i, j
        cdef int r, g, b

        for i in range(0,self.ancho):
            for j in range(0,self.largo):

                r = self.img_o[j,i,0]
                g = self.img_o[j,i,1]
                b = self.img_o[j,i,2]

                new_rgb = ec(r,g,b)

                self.__modificar_rgb(j,i,new_rgb)


    def deshacer_filtro(self):
        ''' Función que deshace los cambios realizados a la imagen'''

        self.img_m[...] = self.img_o


    def gris(self,char tono):
        ''' Función que aplica el filtro gris seleccionado a la imagen

            tono: str. Tono de gris seleccionado para aplicar'''

        if tono == 1:
            self.__modificar_pixeles(lambda r, g, b : tuple([(r + g + b) // 3]*3))
        elif tono == 2:
            self.__modificar_pixeles(lambda r, g, b : tuple([int(r*0.3 + g*0.59 + b*0.11)]*3))
        elif tono == 3:
            self.__modificar_pixeles(lambda r, g, b : tuple([int(r*0.2126 + g*0.7152 + b*0.0722)]*3))
        elif tono == 4:
            self.__modificar_pixeles(lambda r, g, b : tuple([(max(r,g,b) + min(r,g,b)) // 2]*3))
        elif tono == 5:
            self.__modificar_pixeles(lambda r, g, b : tuple([max(r,g,b)]*3))
        elif tono == 6:
            self.__modificar_pixeles(lambda r, g, b : tuple([min(r,g,b)]*3))
        elif tono == 7:
            self.__modificar_pixeles(lambda r, g, b : tuple([r]*3))
        elif tono == 8:
            self.__modificar_pixeles(lambda r, g, b : tuple([g]*3))
        elif tono == 9:
            self.__modificar_pixeles(lambda r, g, b : tuple([b]*3))
        else:
            raise ValueError("Ese tono de gris no existe!")


    def modificar_brillo(self, int cons):
        ''' Función que modifica el brillo de la imagen de acuerdo a la constante recibida

            cons: int. Constante a sumar para modificar el brillo'''

        func = lambda r, g, b: (min(max(int(r+cons), 0), 255),
                                min(max(int(g+cons), 0), 255),
                                min(max(int(b+cons), 0), 255))

        self.__modificar_pixeles(func)


    def __resize_img(self,aux,alto_nuevo,ancho_nuevo):
        ''' Función que cambia el tamaño de la imagen de acuerdo a las nuevas
            medidas recibidas. Regresa la imagen con el tamaño modificado en
            forma de bytes y formarno PNG
            
            alto_nuevo: int. Nueva medida del alto
            ancho_nuevo: int. Nueva medida del ancho
            '''
        w,h = aux.size

        while w > 720 or h > 450:
            scale = min(alto_nuevo/h, ancho_nuevo/w)
            aux = aux.resize((int(w*scale),int(h*scale)),Image.ANTIALIAS)
            alto_nuevo -= 100
            ancho_nuevo -= 100
            w,h = aux.size

        bio = io.BytesIO()
        aux.save(bio,format = "PNG")

        return bio.getvalue()


    def get_img(self,tipo_img):
        ''' Función que regresa la imagen original o modificada con tamaño modificado.

            Si recibe 'o' regresa la imagen original.
            Si recibe 'm' regresa la imagen modificada.
            
            tipo_img: char. Imagen que se requiere regresar'''

        if tipo_img == 'o':
            aux = Image.fromarray(np.array(self.img_o))
        elif tipo_img == 'm':
            aux = Image.fromarray(np.array(self.img_m))

        return self.__resize_img(aux,700,700)


    def guardar(self,ruta):
        ''' Función que guarda la imagen modificada en la ruta ingresada.
        
            Regresa True si se realizó el guardadi exitosmente
            Regresa False si el formato no coincidió
            
            ruta: str. Ruta donde se va a guardar la imagen'''

        img_pil = Image.fromarray(np.array(self.img_m))

        if self.img_formato == 'PNG':
            if ruta.endswith('.png'):
                img_pil.save(ruta,format = self.img_formato)
                return True

        elif self.img_formato == 'JPEG':
            if ruta.endswith((".jpg",".jpeg")):
                img_pil.save(ruta, format = self.img_formato)
                return True

        elif self.img_formato == None:
            img_pil.save(ruta)
            return True

        return False


    def mosaico(self, int num_columnas, int num_filas):
        '''Función que aplica el filtro de mosaico a la imagen

            num_columnas: int. Ancho del mosaico
            num_filas: int. Largo del mosaico '''

        cdef int i,j,c,f
        cdef int[:] new_rgb

        for j in range(0,self.largo,num_filas):
            for i in range(0,self.ancho,num_columnas):    

                if (i + num_columnas > self.ancho) and (j + num_filas > self.largo):
                    new_rgb = self.__color_promedio(i,j,self.ancho,self.largo)

                elif (i + num_columnas > self.ancho):
                    new_rgb = self.__color_promedio(i,j,self.ancho,j+num_filas)

                elif (j + num_filas > self.largo):
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,self.largo)

                else:
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,j+num_filas)

                c = i

                while (c < i + num_columnas) and (c < self.ancho):
                    f = j
                    while (f < j + num_filas) and (f < self.largo):
                        self.__modificar_rgb(f,c,new_rgb)
                        f += 1
                    c += 1


    cdef int[:] __color_promedio(self, int columna_ini, int fila_ini, int columna_fin, int fila_fin):
        ''' Función auxiliar que calcula el color promedio de una parte
        de la imagen.

        Regresa una tupla con los 3 valores nuevos del pixel
        
        columna_ini: int. Valor de la columna inicial
        fila_ini: int. Valor de la fila inicial
        columna_fin: int. Valor de la columna final
        fila_fin: int. Valor de la columna inicial'''

        cdef int total_pixeles = (columna_fin - columna_ini) * (fila_fin - fila_ini)
        cdef int total_r = 0
        cdef int total_g = 0
        cdef int total_b = 0

        cdef int i,j,r,g,b

        for j in range(fila_ini,fila_fin):
            for i in range(columna_ini,columna_fin):

                r = self.img_o[j,i,0]
                g = self.img_o[j,i,1]
                b = self.img_o[j,i,2]

                total_r += r
                total_g += g
                total_b += b

        cdef int[:] prom = np.array((total_r // total_pixeles,
                                     total_g // total_pixeles,
                                     total_b // total_pixeles),dtype=np.intc)

        return prom


    def alto_contraste(self):
        ''' Función que aplica el filtro de alto contraste a la imagen original'''

        self.gris(1)

        func = lambda r, g, b: (255,255,255) if r > 127 and g > 127 and b > 127 else (0,0,0)

        self.__modificar_pixeles(func)

    
    def inverso(self):
        ''' Función que aplica el filtro inverso a la imagen original'''

        self.gris(1)

        func = lambda r, g, b: (0,0,0) if r > 127 and g > 127 and b > 127 else (255,255,255)

        self.__modificar_pixeles(func)


    def capa_rgb(self, int new_r, int new_g, int new_b):
        ''' Función que aplica la capa RGB con los valores recibidos a 
        la imagen original
        
        new_r: int. Valor del color rojo
        new_g: int. Valor del color verde
        new_b: int. Valor del color azul'''
        
        func = lambda r, g, b: (new_r & r,new_g & g,new_b & b)

        self.__modificar_pixeles(func)


    cdef void __aplicar_convolucion(self, int[:, :] filtro, double factor, double brillo):
        ''' Función que aplica a la imagen el filtro de convolución con el valor
            de brillo y factor recibidos
            
            filtro: list. Matriz del filtro de convolución
            factor: int. Valor del factor para aplicar el filtro
            brillo: int. Valor del brillo'''

        cdef int x,y
        cdef int suma_r, suma_g, suma_b,f_x,f_y
        cdef int img_x,img_y,r,g,b

        cdef int[:] new_rgb

        for y in range(0,self.largo):
            for x in range(0,self.ancho):
                
                suma_r = suma_g = suma_b = 0

                for f_y in range(0,len(filtro)):
                    for f_x in range(0,len(filtro[0])):
                        
                        img_x = int((x - len(filtro[0]) / 2 + f_x + self.ancho) % self.ancho)
                        img_y = int((y - len(filtro) / 2 + f_y + self.largo) % self.largo)

                        r = self.img_o[img_y,img_x,0]
                        g = self.img_o[img_y,img_x,1]
                        b = self.img_o[img_y,img_x,2]

                        suma_r += r * filtro[f_y][f_x]
                        suma_g += g * filtro[f_y][f_x]
                        suma_b += b * filtro[f_y][f_x]
                    
                new_rgb = np.array((min(max(int(factor * suma_r + brillo), 0), 255),
                                    min(max(int(factor * suma_g + brillo), 0), 255),
                                    min(max(int(factor * suma_b + brillo), 0), 255)), dtype = np.intc)

                self.__modificar_rgb(y,x,new_rgb)


    cdef void __aplicar_convolucion_d(self, double[:, :] filtro, double factor, double brillo):
        ''' Función que aplica a la imagen el filtro de convolución con el valor
            de brillo y factor recibidos
            
            filtro: list. MatSriz del filtro de convolución
            factor: int. Valor del factor para aplicar el filtro
            brillo: int. Valor del brillo'''

        cdef int x,y
        cdef double suma_r, suma_g, suma_b
        cdef int img_x,img_y,f_x,f_y,r,g,b

        cdef int[:] new_rgb

        for y in range(0,self.largo):
            for x in range(0,self.ancho):

                suma_r = suma_g = suma_b = 0

                for f_y in range(0,len(filtro)):
                    for f_x in range(0,len(filtro[0])):
                        
                        img_x = int((x - len(filtro[0]) / 2 + f_x + self.ancho) % self.ancho)
                        img_y = int((y - len(filtro) / 2 + f_y + self.largo) % self.largo)

                        r = self.img_o[img_y,img_x,0]
                        g = self.img_o[img_y,img_x,1]
                        b = self.img_o[img_y,img_x,2]

                        suma_r += r * filtro[f_y][f_x]
                        suma_g += g * filtro[f_y][f_x]
                        suma_b += b * filtro[f_y][f_x]
                    
                new_rgb = np.array((min(max(int(factor * suma_r + brillo), 0), 255),
                                    min(max(int(factor * suma_g + brillo), 0), 255),
                                    min(max(int(factor * suma_b + brillo), 0), 255)), dtype = np.intc)

                self.__modificar_rgb(y,x,new_rgb)


    def filtros_convolucion(self,filtro):
        ''' Funcion que recibe un tipo de filtro de convolución y lo aplica con la matriz
            y valores correspondientes
            
            filtro: str. Filtro seleccionado que se va a aplicar'''

        if filtro == 'Suave':
            self.__aplicar_convolucion_d(
                np.array([[0.0,0.2,0.0],
                 [0.2,0.2,0.2],
                 [0.0,0.2,0.0]],dtype=np.double), 1.0, 0.0
            )
        elif filtro == 'Fuerte':
            self.__aplicar_convolucion(
                np.array([[0,0,1,0,0],
                 [0,1,1,1,0],
                 [1,1,1,1,1],
                 [0,1,1,1,0],
                 [0,0,1,0,0]],dtype=np.intc), 1.0 / 13.0, 0.0
            )
        elif filtro == 'Motion Blur':
            self.__aplicar_convolucion(
                np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 1, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 1, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 1, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1]],dtype=np.intc), 1.0 / 9.0, 0.0
            )
        elif filtro == 'Encontrar bordes':
            self.__aplicar_convolucion(
               np.array([[-1,  0, 0,  0,  0],
                [ 0, -2, 0,  0,  0],
                [ 0,  0, 6,  0,  0],
                [ 0,  0, 0, -2,  0],
                [ 0,  0, 0,  0, -1]],dtype=np.intc), 1.0, 0.0
            )
        elif filtro == 'Sharpen':
            self.__aplicar_convolucion(
               np.array([[-1, -1, -1],
                [-1,  9, -1],
                [-1, -1, -1]],dtype=np.intc), 1.0, 0.0
            )
        elif filtro == 'Emboss':
            self.__aplicar_convolucion(
               np.array([[-1, -1, -1, -1, 0],
                [-1, -1, -1,  0, 1],
                [-1, -1,  0,  1, 1],
                [-1,  0,  1,  1, 1],
                [ 0,  1,  1,  1, 1]],dtype=np.intc), 1.0, 128.0
            )
        else:
            raise ValueError("Ese filtro de convolucion no existe!")