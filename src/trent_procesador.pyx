# cython: language_level=3
import io
import sys
import os.path
import numpy as np
import PySimpleGUI as sg
from shutil import rmtree
from PIL import Image,ImageDraw,ImageFont
from tkinter import Tk,Canvas

cdef class PDI:
    ''' Clase que se encarga de la lógica de cada uno de los filtros y modificaciones'''

    cdef unsigned char[:, :, :] img_o  # Imagen original transformada a arreglo
    cdef unsigned char[:, :, :] img_m  # Imagen modificada
    cdef int ancho                     # Número de pixeles a lo ancho de la imagen original
    cdef int alto                     # Número de pixeles a lo alto de la imagen original
    cdef str img_formato               # Formato de la imagen original

    def __cinit__(self, ruta):
        ''' Carga la imagen en un arreglo de acuerdo a la ruta 

            ruta: str. Ruta de la imagen '''

        self.img_formato = Image.open(ruta).format 
        self.img_o = np.array(Image.open(ruta))            
        self.img_m = self.img_o.copy()             
        self.ancho = np.size(self.img_o,axis = 1)  
        self.alto = np.size(self.img_o,axis = 0)  


    def __modificar_rgb(self, int x, int y, rgb):
        '''Función que modifica los valores RGB del pixel en la posición (x,y) 
            x: int. Posición x del pixel
            y: int. Posición y del pixel
            rgb: list. Lista con los 3 nuevos valores del pixel'''

        cdef int z

        for z in range(0,3):
            self.img_m[x,y,z] = rgb[z]


    def __modificar_pixeles(self, ec, pb, img):
        ''' Función que aplica la función recibida a los valores RGB del pixel y
            los nuevos valores generados por esta función se aplican al pixel

            ec. function. Función a aplicar
            br. boolean. Valor que indica si crear o no una barra de progreso'''

        cdef int i, j
        cdef int r, g, b
        cdef int ancho_m = np.size(self.img_m,axis = 1)
        cdef int alto_m = np.size(self.img_m,axis = 0)

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = (self.ancho * self.alto) / 20

        if pb:
            win = self.__crear_barra_de_progreso()
            pb = win.FindElement('progress')
        # Variables de la barra de progreso. Fin

        for i in range(0,ancho_m):
            for j in range(0,alto_m):

                if img:
                    r = self.img_o[j,i,0]
                    g = self.img_o[j,i,1]
                    b = self.img_o[j,i,2]
                else:
                    r = self.img_m[j,i,0]
                    g = self.img_m[j,i,1]
                    b = self.img_m[j,i,2]

                new_rgb = ec(r,g,b)

                self.__modificar_rgb(j,i,new_rgb)

            if pb:
                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += (self.ancho * self.alto) / 20

                num_pixel += 1
                # Avance barra de progreso. Fin              
        if pb:
            win.close()

    def __crear_barra_de_progreso(self):
        ''' '''

        total_pixeles = self.ancho * self.alto

        layout_bp = [[sg.Text('Procesando...')],
              [sg.ProgressBar(100,orientation='h',size=(20, 20),key='progress')],
        ]
        
        window = sg.Window('Aplicando filtro', layout_bp).Finalize()

        return window


    def deshacer_filtro(self):
        ''' Función que deshace los cambios realizados a la imagen'''

        self.img_m = self.img_o.copy()


    def gris(self, char tono, bint br):
        ''' Función que aplica el filtro gris seleccionado a la imagen

            tono: str. Tono de gris seleccionado para aplicar'''

        if tono == 1:
            self.__modificar_pixeles(lambda r, g, b : tuple([(r + g + b) // 3]*3),br,True)
        elif tono == 2:
            self.__modificar_pixeles(lambda r, g, b : tuple([int(r*0.3 + g*0.59 + b*0.11)]*3),br,True)
        elif tono == 3:
            self.__modificar_pixeles(lambda r, g, b : tuple([int(r*0.2126 + g*0.7152 + b*0.0722)]*3),br,True)
        elif tono == 4:
            self.__modificar_pixeles(lambda r, g, b : tuple([(max(r,g,b) + min(r,g,b)) // 2]*3),br,True)
        elif tono == 5:
            self.__modificar_pixeles(lambda r, g, b : tuple([max(r,g,b)]*3),br,True)
        elif tono == 6:
            self.__modificar_pixeles(lambda r, g, b : tuple([min(r,g,b)]*3),br,True)
        elif tono == 7:
            self.__modificar_pixeles(lambda r, g, b : tuple([r]*3),br,True)
        elif tono == 8:
            self.__modificar_pixeles(lambda r, g, b : tuple([g]*3),br,True)
        elif tono == 9:
            self.__modificar_pixeles(lambda r, g, b : tuple([b]*3),br,True)
        else:
            raise ValueError("Ese tono de gris no existe!")


    def modificar_brillo(self, int cons, bint br, bint img):
        ''' Función que modifica el brillo de la imagen de acuerdo a la constante recibida

            cons: int. Constante a sumar para modificar el brillo'''

        func = lambda r, g, b: (min(max(int(r+cons), 0), 255),
                                min(max(int(g+cons), 0), 255),
                                min(max(int(b+cons), 0), 255))

        self.__modificar_pixeles(func,br,img)


    def __resize_img(self,aux,alto_nuevo,ancho_nuevo):
        ''' Función que cambia el tamanio de la imagen de acuerdo a las nuevas
            medidas recibidas. Regresa la imagen con el tamanio modificado en
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
        ''' Función que regresa la imagen original o modificada con tamanio modificado.

            Si recibe 'o' regresa la imagen original.
            Si recibe 'm' regresa la imagen modificada.
            
            tipo_img: char. Imagen que se requiere regresar'''

        if tipo_img == 'o':
            aux = Image.fromarray(np.array(self.img_o))
        elif tipo_img == 'm':
            aux = Image.fromarray(np.array(self.img_m))

        return self.__resize_img(aux,700,700)


    def get_tamanio(self):
        ''' Función que regresa el tamanio de la imagen original'''
        return (self.ancho,self.alto)


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
            num_filas: int. alto del mosaico '''

        cdef int i,j,c,f
        cdef int[:] new_rgb

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = ((self.ancho/num_columnas) * (self.alto/num_filas)) / 20

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')
        # Variables de la barra de progreso. Fin

        for j in range(0,self.alto,num_filas):
            for i in range(0,self.ancho,num_columnas):    

                if (i + num_columnas > self.ancho) and (j + num_filas > self.alto):
                    new_rgb = self.__color_promedio(i,j,self.ancho,self.alto,False)

                elif (i + num_columnas > self.ancho):
                    new_rgb = self.__color_promedio(i,j,self.ancho,j+num_filas,False)

                elif (j + num_filas > self.alto):
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,self.alto,False)

                else:
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,j+num_filas,False)

                c = i

                while (c < i + num_columnas) and (c < self.ancho):
                    f = j
                    while (f < j + num_filas) and (f < self.alto):
                        self.__modificar_rgb(f,c,new_rgb)
                        f += 1
                    c += 1

                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += ((self.ancho/num_columnas) * (self.alto/num_filas)) / 20

                num_pixel += 1
                # Avance barra de progreso. Fin

        win.close()

    cdef int[:] __color_promedio(self, int columna_ini, int fila_ini, int columna_fin, int fila_fin, bint doble_f):
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
        cdef unsigned char[:, :, :] aux

        if doble_f:
            aux = self.img_m
        else:
            aux = self.img_o

        for j in range(fila_ini,fila_fin):
            for i in range(columna_ini,columna_fin):

                r = aux[j,i,0]
                g = aux[j,i,1]
                b = aux[j,i,2]

                total_r += r
                total_g += g
                total_b += b

        cdef int[:] prom = np.array((total_r // total_pixeles,
                                     total_g // total_pixeles,
                                     total_b // total_pixeles),dtype=np.intc)

        return prom


    def alto_contraste(self, bint br):
        ''' Función que aplica el filtro de alto contraste a la imagen original'''

        self.gris(1)

        func = lambda r, g, b: (255,255,255) if r > 127 and g > 127 and b > 127 else (0,0,0)

        self.__modificar_pixeles(func,br,True)

    
    def inverso(self, bint br):
        ''' Función que aplica el filtro inverso a la imagen original'''

        self.gris(1)

        func = lambda r, g, b: (0,0,0) if r > 127 and g > 127 and b > 127 else (255,255,255)

        self.__modificar_pixeles(func,br,True)


    def capa_rgb(self, int new_r, int new_g, int new_b, bint br, bint img):
        ''' Función que aplica la capa RGB con los valores recibidos a 
        la imagen original
        
        new_r: int. Valor del color rojo
        new_g: int. Valor del color verde
        new_b: int. Valor del color azul'''
        
        func = lambda r, g, b: (new_r & r,new_g & g,new_b & b)

        self.__modificar_pixeles(func,br,img)


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

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = (self.ancho * self.alto) / 20

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')  
        # Variables de la barra de progreso. Fin        

        for y in range(0,self.alto):
            for x in range(0,self.ancho):
                
                suma_r = suma_g = suma_b = 0

                for f_y in range(0,len(filtro)):
                    for f_x in range(0,len(filtro[0])):
                        
                        img_x = int((x - len(filtro[0]) / 2 + f_x + self.ancho) % self.ancho)
                        img_y = int((y - len(filtro) / 2 + f_y + self.alto) % self.alto)

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
                
                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += (self.ancho * self.alto) / 20

                num_pixel += 1                
                # Avance barra de progreso. Fin

        win.close()                     


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

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = (self.ancho * self.alto) / 20

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')        
        # Variables de la barra de progreso. Fin

        for y in range(0,self.alto):
            for x in range(0,self.ancho):

                suma_r = suma_g = suma_b = 0

                for f_y in range(0,len(filtro)):
                    for f_x in range(0,len(filtro[0])):
                        
                        img_x = int((x - len(filtro[0]) / 2 + f_x + self.ancho) % self.ancho)
                        img_y = int((y - len(filtro) / 2 + f_y + self.alto) % self.alto)

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

                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += (self.ancho * self.alto) / 20

                num_pixel += 1                
                # Avance barra de progreso. Fin

        win.close()                


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


    def __selecciona_letra(self, int t_gris):
        ''' Función que regresa una letra de acuerdo al tono de gris ingresado
            
            t_gris: int. Valor de tono de gris'''

        if 0 <= t_gris < 16:
            return 'M'
        elif 16 <= t_gris < 32:
            return 'N'
        elif 32 <= t_gris < 48:
            return 'H'
        elif 48 <= t_gris < 64:
            return '#'
        elif 64 <= t_gris < 80:
            return 'Q'
        elif 80 <= t_gris < 96:
            return 'U'
        elif 96 <= t_gris < 112:
            return 'A'
        elif 112 <= t_gris < 128:
            return 'D'
        elif 128 <= t_gris < 144:
            return '0'
        elif 144 <= t_gris < 160:
            return 'Y'
        elif 160 <= t_gris < 176:
            return '2'
        elif 176 <= t_gris < 192:
            return '$'
        elif 192 <= t_gris < 210:
            return '%'
        elif 210 <= t_gris < 226:
            return '+'
        elif 226 <= t_gris < 240:
            return '.'
        elif 240 <= t_gris < 256:
            return ' '


    def __selecciona_domino_b(self, int tono, int cont):
        ''' Funcion que regresa una letra con fuente de letra de domino
            blanco de acuerdo al valor del tono y si se necesita ficha 
            izquierda o derecha
            
            tono: int. Valor del tono 
            cont: int. Contador de letras colocadas'''

        if (cont + 1) % 2 == 0:
            if 0 <= tono < 37:
                return '^'
            elif 37 <= tono < 73:
                return '%'
            elif 73 <= tono < 109:
                return '$'
            elif 109 <= tono < 145:
                return '#'
            elif 145 <= tono < 181:
                return '@'
            elif 181 <= tono < 217:
                return '!'
            elif 217 <= tono < 256:
                return ')'
        else:
            if 0 <= tono < 37:
                return '6'
            elif 37 <= tono < 73:
                return '5'
            elif 73 <= tono < 109:
                return '4'
            elif 109 <= tono < 145:
                return '3'
            elif 145 <= tono < 181:
                return '2'
            elif 181 <= tono < 217:
                return '1'
            elif 217 <= tono < 256:
                return '0'


    def __selecciona_domino_n(self, int tono, int cont):
        ''' Funcion que regresa una letra con fuente de letra de domino
            negro de acuerdo al valor del tono y si se necesita ficha 
            izquierda o derecha
            
            tono: int. Valor del tono 
            cont: int. Contador de letras colocadas'''

        if (cont + 1) % 2 == 0:
            if 0 <= tono < 37:
                return ')'
            elif 37 <= tono < 73:
                return '!'
            elif 73 <= tono < 109:
                return '@'
            elif 109 <= tono < 145:
                return '#'
            elif 145 <= tono < 181:
                return '$'
            elif 181 <= tono < 217:
                return '%'
            elif 217 <= tono < 256:
                return '^'
        else:
            if 0 <= tono < 37:
                return '0'
            elif 37 <= tono < 73:
                return '1'
            elif 73 <= tono < 109:
                return '2'
            elif 109 <= tono < 145:
                return '3'
            elif 145 <= tono < 181:
                return '4'
            elif 181 <= tono < 217:
                return '5'
            elif 217 <= tono < 256:
                return '6'


    def __selecciona_naipe(self, int t_gris):
        ''' Función que regresa una letra de acuerdo al tono de gris ingresado
            
            t_gris: int. Valor de tono de gris'''

        if 0 <= t_gris < 26:
            return 'J'
        elif 26 <= t_gris < 51:
            return 'I'
        elif 51 <= t_gris < 76:
            return 'H'
        elif 76 <= t_gris < 101:
            return 'G'
        elif 101 <= t_gris < 126:
            return 'F'
        elif 126 <= t_gris < 151:
            return 'E'
        elif 151 <= t_gris < 176:
            return 'D'
        elif 176 <= t_gris < 201:
            return 'C'
        elif 201 <= t_gris < 226:
            return 'B'
        elif 226 <= t_gris < 256:
            return 'A'


    def coloca_letra(self, d, int i, int j, int[:] new_rgb, int cont, opcion, fnt, texto):
        ''' Función que dibuja una letra en la posición indicada y se 
            modifica de acuerdo a la opcion seleccionada por el usuario
            
            d: ImageDraw. Canvas para dibujar las letras
            i: int. Valor de x en el canvas
            j: int. Valor de y en el canvas
            new_rgb: int. Color promedio de la cuadricula
            cont: int. Contador de letras colocadas
            opcion: str. Opcion seleccionada por el ususario
            texto: str. Texto personalizado ingresado por el usuario'''

        cdef int r,g,b

        if opcion.startswith('m'):
            d.text((i,j),'M',fill=tuple(new_rgb),font=fnt)
            
        elif opcion == 'ds-t':
            d.text((i,j),self.__selecciona_letra(new_rgb[0]),fill=(0,0,0),font=fnt)

        elif opcion == 'ds-c':
            r = new_rgb[0]
            g = new_rgb[1]
            b = new_rgb[2]

            d.text((i,j),self.__selecciona_letra((r + g + b) // 3),fill=tuple(new_rgb),font=fnt)

        elif opcion == 'ds-g':
            d.text((i,j),self.__selecciona_letra(new_rgb[0]),fill=tuple(new_rgb),font=fnt)

        elif opcion == 'tp-cl':
            d.text((i,j),texto[cont % len(texto)],fill=tuple(new_rgb),font=fnt)

        elif opcion == 'db':
            d.text((i,j),self.__selecciona_domino_b(new_rgb[0],cont),fill=(0,0,0),font=fnt)

        elif opcion == 'dn':
            d.text((i,j),self.__selecciona_domino_n(new_rgb[0],cont),fill=(0,0,0),font=fnt)

        elif opcion == 'nps':
            d.text((i,j),self.__selecciona_naipe(new_rgb[0]),fill=(0,0,0),font=fnt)


    def __ruta_recurso(self, rtv):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, rtv)


    def selecciona_fuente(self, opcion):
        ''' Funcion que selecciona la fuente de letra de acuerdo
            a la opcion elegida
            
            opcion: str. Opcion elegida por el usuario'''

        if opcion == 'db':
            return ImageFont.truetype(self.__ruta_recurso('fonts/Lasvwd__.otf'),11)
        elif opcion == 'dn':
            return ImageFont.truetype(self.__ruta_recurso('fonts/Lasvbld_.otf'),11)
        elif opcion == 'nps':
            return ImageFont.truetype(self.__ruta_recurso('fonts/PLAYCRDS.otf'),17)
        else:
            return ImageFont.truetype(self.__ruta_recurso('fonts/Minecraft.ttf'),10)


    def genera_texto(self, int num_columnas, int num_filas, bint doble_f, opcion, texto = None):
        ''' Función que cuadricula la imagen, calcula el color promedio de 
            cada region y por cada una de ellas genera el texto indicado
            del color promedio correpondiente

            num_columnas: int. Ancho de la seccion
            num_filas: int. alto de la seccion 
            doble_f: bint. Valor que determina si se van aplicar dos filtros
                           consecutivos
            opcion: str. Opcion seleccionada por el usuario
            texto: str. Texto personalizado ingresado por el usuario'''

        fnt = self.selecciona_fuente(opcion)

        img_letras = Image.new("RGB",(self.ancho,self.alto),(255, 255, 255))
        l = ImageDraw.Draw(img_letras)

        cdef int i,j,c
        cdef int[:] new_rgb

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = ((self.ancho/num_columnas) * (self.alto/num_filas)) / 20
        # Variables de la barra de progreso. Fin

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')

        c = 0

        for j in range(0,self.alto,num_filas):
            for i in range(0,self.ancho,num_columnas):

                if (i + num_columnas > self.ancho) and (j + num_filas > self.alto):
                    new_rgb = self.__color_promedio(i,j,self.ancho,self.alto,doble_f)

                elif (i + num_columnas > self.ancho):
                    new_rgb = self.__color_promedio(i,j,self.ancho,j+num_filas,doble_f)

                elif (j + num_filas > self.alto):
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,self.alto,doble_f)

                else:
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,j+num_filas,doble_f)
                
                self.coloca_letra(l,i,j,new_rgb,c,opcion,fnt,texto)

                c += 1

                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += ((self.ancho/num_columnas) * (self.alto/num_filas)) / 20

                num_pixel += 1
                # Avance barra de progreso. Fin
                
        win.close()
        self.img_m = np.array(img_letras)


    def filtros_letras(self, num_columnas, num_filas, opcion, txt = None):
        ''' Funcion que realiza la llamada correspondiente para generar texto 
            en el canvas de acuerdo a la opcion seleccionada
            
            num_columnas: int. Ancho de la seccion
            num_filas: int. alto de la seccion             
            opcion: str. Opcion seleccionada por el usuario
            txt: str. Texto personalizado ingresado por el usuario
            '''
        if opcion in ['m-cl','ds-c','tp-cl']:
            self.genera_texto(num_columnas,num_filas,False,opcion,txt)

        if opcion in ['m-g','ds-t','ds-g','dn','db','nps']:
            self.gris(1)
            self.genera_texto(num_columnas,num_filas,True,opcion)


    def __genera_img_texto(self, texto, estilo, int x, int y):
        ''' Funcion que crea una imagen en blanco del mismo tamanio que la original
            con el texto personalizado en las coordenadas indicadas
            
            texto: str. Texto que se va a escribir en la imagen
            estilo: tuple. Tupla con la ruta y el tamaño de la fuente
            x: int. Coordenada x en la imagen
            y: int. Coordenada y en la imagen'''

        img_texto = Image.new("RGB",(self.ancho,self.alto),(255, 255, 255))
        draw_texto = ImageDraw.Draw(img_texto)

        ruta = estilo[0]
        tmn = estilo[1]

        fnt = ImageFont.truetype(ruta,tmn)

        draw_texto.text((x,y),texto,font = fnt, fill = (0,0,0))

        return img_texto
        

    def marca_de_agua(self, texto, estilo, int x, int y):
        ''' Funcion que procesa la imagen modificada y la imagen en blanco
            con texto para crear la marca de agua
        
            texto: str. Texto de la marca de agua
            estilo: tuple. Tupla con la ruta y el tamaño de la fuente
            x: int. Coordenada x en la imagen
            y: int. Coordenada y en la imagen'''

        img_texto = np.array(self.__genera_img_texto(texto,estilo,x,y))

        cdef int i, j
        cdef int r, g, b, n_r, n_g, n_b
        cdef double alpha = estilo[2] / 100

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = (self.ancho * self.alto) / 20
        # Variables de la barra de progreso. Fin

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')

        for i in range(0,self.ancho):
            for j in range(0,self.alto):

                r_img = self.img_m[j,i,0]
                g_img = self.img_m[j,i,1]
                b_img = self.img_m[j,i,2]

                r_txt = img_texto[j,i,0]
                g_txt = img_texto[j,i,1]
                b_txt = img_texto[j,i,2]

                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += (self.ancho * self.alto) / 20

                num_pixel += 1
                # Avance barra de progreso. Fin

                if r_txt == 255 & g_txt == 255 & b_txt == 255:
                    continue
                else:
                    n_r = int(r_img * alpha + r_txt * (1.0 - alpha))
                    n_g = int(g_img * alpha + g_txt * (1.0 - alpha))
                    n_b = int(b_img * alpha + b_txt * (1.0 - alpha))

                    self.__modificar_rgb(j,i,(n_r,n_g,n_b))

        win.close()


    def selecciona_imagen(self, tono):
        pass


    def imgs_recursivas_gris(self, int ancho, int alto, int num_columnas, int num_filas):

        try:
            rmtree("./out/gris")
            os.makedirs("./out/gris",exist_ok=True)
        except:
            os.makedirs("./out/gris",exist_ok=True)
            pass

        cdef int i,j
        cdef int[:] new_rgb
        cdef int brillo = -180

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef double pb_progress = 1.5

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')
        # Variables de la barra de progreso. Fin        

        img_recursiva = Image.fromarray(np.array(self.img_m),'RGB').resize((ancho,alto),Image.ANTIALIAS)

        self.img_m = np.array(img_recursiva)

        for i in range(30):
            self.modificar_brillo(brillo,False,False)
            img_pil = Image.fromarray(np.array(self.img_m),'RGB')

            if self.img_formato == None:
                img_pil.save('out/gris/' + str(i+1) + '.' + 'PNG',quality = 95)
            else:
                img_pil.save('out/gris/' + str(i+1) + '.' + self.img_formato,quality = 95)

            brillo += 12

            self.img_m = np.array(img_recursiva)

            # Avance barra de progreso. Inicio
            if i == int(pb_progress):
                pb.update(pb_value)
                pb_value += 5
                pb_progress += 1.5
            # Avance barra de progreso. Fin

        self.deshacer_filtro()
        win.close()

        
    def __rgb_to_hex(self, rgb):
        return '%02x%02x%02x' % rgb


    def imgs_recursivas_color(self, int ancho, int alto, int num_columnas, int num_filas):

        try:
            rmtree("./out/color")
            os.makedirs("./out/color",exist_ok=True)
        except:
            os.makedirs("./out/color",exist_ok=True)
            pass

        cdef int i,j,r,g,b
        cdef int[:] new_rgb

        cache = []

        # Variables de la barra de progreso. Inicio
        cdef int pb_value = 5
        cdef int num_pixel = 1
        cdef double pb_progress = ((self.ancho/num_columnas) * (self.alto/num_filas)) / 20

        win = self.__crear_barra_de_progreso()
        pb = win.FindElement('progress')
        # Variables de la barra de progreso. Fin

        img_recursiva = Image.fromarray(np.array(self.img_m)).resize((ancho,alto),Image.ANTIALIAS)

        self.img_m = np.array(img_recursiva)        

        for j in range(0,self.alto,num_filas):
            for i in range(0,self.ancho,num_columnas):    

                if (i + num_columnas > self.ancho) and (j + num_filas > self.alto):
                    new_rgb = self.__color_promedio(i,j,self.ancho,self.alto,False)

                elif (i + num_columnas > self.ancho):
                    new_rgb = self.__color_promedio(i,j,self.ancho,j+num_filas,False)

                elif (j + num_filas > self.alto):
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,self.alto,False)

                else:
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,j+num_filas,False)

                r = new_rgb[0]
                g = new_rgb[1]
                b = new_rgb[2]

                self.capa_rgb(r,g,b,False,False)

                img_pil = Image.fromarray(np.array(self.img_m),'RGB')

                nombre = self.__rgb_to_hex(tuple(new_rgb))

                if nombre not in cache:
                    if self.img_formato == None:
                        img_pil.save('out/color/' + nombre + '.' + 'PNG',quality=95)
                    else:
                        img_pil.save('out/color/' + nombre + '.' + self.img_formato,quality=95)

                    cache.append(nombre)

                # Avance barra de progreso. Inicio
                if num_pixel == int(pb_progress):
                    pb.update(pb_value)
                    pb_value += 5
                    pb_progress += ((self.ancho/num_columnas) * (self.alto/num_filas)) / 20

                num_pixel += 1
                # Avance barra de progreso. Fin

                self.img_m = np.array(img_recursiva)

        win.close()

