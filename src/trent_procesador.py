from PIL import Image
import io
import numpy as np

class PDI(object):
    ''' Clase que se encarga de la lógica de cada uno de los filtros y modificaciones'''

    def __init__(self, ruta):
        ''' Carga la imagen de acuerdo a la ruta 

            ruta: str. Ruta de la imagen '''

        self.img_o = Image.open(ruta)                  # Imagen original
        self.img_array = np.array(self.img_o)          # Imagen original transformada a arreglo
        self.img_m = self.img_array.copy()             # Imagen modificada
        self.ancho = np.size(self.img_array,axis = 1)  # Número de pixeles a lo ancho de la imagen original
        self.largo = np.size(self.img_array,axis = 0)  # Número de pixeles a lo largo de la imagen original

    def __modificar_rgb(self,x,y,rgb):
        '''Función que modifica los valores RGB del pixel en la posición (x,y) 
            x: int. Posición x del pixel
            y: int. Posición y del pixel
            rgb: list. Lista con los 3 nuevos valores del pixel'''

        for z in range(0,3):
            self.img_m.itemset((x,y,z),rgb[z])


    def __modificar_pixeles(self,ec):
        ''' Función que aplica la función recibida a los valores RGB del pixel y
            los nuevos valores generados por esta función se aplican al pixel

            ec. function. Función a aplicar'''

        for i in range(0,self.ancho):
            for j in range(0,self.largo):

                r = self.img_array.item(j,i,0)
                g = self.img_array.item(j,i,1)
                b = self.img_array.item(j,i,2)

                new_rgb = ec(r,g,b)

                self.__modificar_rgb(j,i,new_rgb)


    def __aplicar_filtro(self,ec):
        ''' Función que recibe una ecuación en forma de lambda para ser aplicada
            a todos los pixeles de la imagen

            ec: function. Lambda a aplicar'''

        for i in range(0,self.ancho):
            for j in range(0,self.largo):

                r = self.img_array.item(j,i,0)
                g = self.img_array.item(j,i,1)
                b = self.img_array.item(j,i,2)

                value = ec(r,g,b)

                self.__modificar_rgb(j,i,(value,value,value))


    def deshacer_filtro(self):
        ''' Función que deshace los cambios realizados a la imagen'''

        self.img_m = self.img_array.copy()


    def gris(self,tono):
        ''' Función que aplica el filtro gris seleccionado a la imagen

            tono: str. Tono de gris seleccionado para aplicar'''

        if tono == 'Tono 1':
            self.__aplicar_filtro(lambda r, g, b : (r + g + b) // 3)
        elif tono == 'Tono 2':
            self.__aplicar_filtro(lambda r, g, b : int(r*0.3 + g*0.59 + b*0.11))
        elif tono == 'Tono 3':
            self.__aplicar_filtro(lambda r, g, b : int(r*0.2126 + g*0.7152 + b*0.0722) )
        elif tono == 'Tono 4':
            self.__aplicar_filtro(lambda r, g, b : (max(r,g,b) + min(r,g,b)) // 2)
        elif tono == 'Tono 5':
            self.__aplicar_filtro(lambda r, g, b : max(r,g,b))
        elif tono == 'Tono 6':
            self.__aplicar_filtro(lambda r, g, b : min(r,g,b))
        elif tono == 'Tono 7':
            self.__aplicar_filtro(lambda r, g, b : r)
        elif tono == 'Tono 8':
            self.__aplicar_filtro(lambda r, g, b : g)
        elif tono == 'Tono 9':
            self.__aplicar_filtro(lambda r, g, b : b)
        else:
            raise ValueError("Ese tono de gris no existe!")


    def modificar_brillo(self,cons):
        ''' Función que modifica el brillo de la imagen de acuerdo a la constante recibida

            cons: int. Constante a sumar para modificar el brillo'''

        for i in range(0,self.ancho):
            for j in range(0,self.largo):

                r = self.img_array.item(j,i,0)
                g = self.img_array.item(j,i,1)
                b = self.img_array.item(j,i,2)

                n_r = 0 if (r+cons) < 0 else 255 if (r+cons) > 255 else int(r+cons)
                n_g = 0 if (g+cons) < 0 else 255 if (g+cons) > 255 else int(g+cons)
                n_b = 0 if (b+cons) < 0 else 255 if (b+cons) > 255 else int(b+cons)

                self.__modificar_rgb(j,i,(n_r,n_g,n_b))


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
            aux = self.img_o.copy()
        elif tipo_img == 'm':
            aux = Image.fromarray(self.img_m)

        return self.__resize_img(aux,700,700)


    def guardar(self,ruta):
        ''' Función que guarda la imagen modificada en la ruta ingresada.
        
            Regresa True si se realizó el guardadi exitosmente
            Regresa False si el formato no coincidió
            
            ruta: str. Ruta donde se va a guardar la imagen'''

        img_pil = Image.fromarray(self.img_m)

        if self.img_o.format == 'PNG':
            if ruta.endswith('.png'):
                img_pil.save(ruta,format = self.img_o.format)
                return True

        elif self.img_o.format == 'JPEG':
            if ruta.endswith((".jpg",".jpeg")):
                img_pil.save(ruta, format = self.img_o.format)
                return True

        elif self.img_o.format == None:
            img_pil.save(ruta)
            return True

        return False


    def mosaico(self,num_columnas,num_filas):
        '''Función que aplica el filtro de mosaico a la imagen

            num_columnas: int. Ancho del mosaico
            num_filas: int. Largo del mosaico '''

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

        

    def __color_promedio(self,columna_ini,fila_ini,columna_fin,fila_fin):
        ''' Función auxiliar que calcula el color promedio de una parte
        de la imagen.

        Regresa una tupla con los 3 valores nuevos del pixel
        
        columna_ini: int. Valor de la columna inicial
        fila_ini: int. Valor de la fila inicial
        columna_fin: int. Valor de la columna final
        fila_fin: int. Valor de la columna inicial'''

        total_pixeles = (columna_fin - columna_ini) * (fila_fin - fila_ini)
        total_r = 0
        total_g = 0
        total_b = 0

        for j in range(fila_ini,fila_fin):
            for i in range(columna_ini,columna_fin):

                r = self.img_array.item(j,i,0)
                g = self.img_array.item(j,i,1)
                b = self.img_array.item(j,i,2)

                total_r += r
                total_g += g
                total_b += b

        return (total_r // total_pixeles,total_g // total_pixeles,total_b // total_pixeles)


    def alto_contraste(self):
        ''' Función que aplica el filtro de alto contraste a la imagen original'''

        self.gris('Tono 1')

        func = lambda r, g, b: (255,255,255) if r > 127 and g > 127 and b > 127 else (0,0,0)

        self.__modificar_pixeles(func)

    
    def inverso(self):
        ''' Función que aplica el filtro inverso a la imagen original'''

        self.gris('Tono 1')

        func = lambda r, g, b: (0,0,0) if r > 127 and g > 127 and b > 127 else (255,255,255)

        self.__modificar_pixeles(func)


    def modifica_rgb(self,new_r,new_g,new_b):
        ''' Función que aplica la capa RGB con los valores recibidos a 
        la imagen original
        
        new_r: int. Valor del color rojo
        new_g: int. Valor del color verde
        new_b: int. Valor del color azul'''
        
        func = lambda r, g, b: (new_r & r,new_g & g,new_b & b)

        self.__modificar_pixeles(func)


    def __aplicar_convolucion(self,filtro,factor,brillo):
        ''' Función que aplica a la imagen el filtro de convolución con el valor
            de brillo y factor recibidos
            
            filtro: list. Matriz del filtro de convolución
            factor: int. Valor del factor para aplicar el filtro
            brillo: int. Valor del brillo'''

        for y in range(0,self.largo):
            for x in range(0,self.ancho):

                suma_r = suma_g = suma_b = 0

                for f_y in range(0,len(filtro)):
                    for f_x in range(0,len(filtro[0])):
                        
                        img_x = int((x - len(filtro[0]) / 2 + f_x + self.ancho) % self.ancho)
                        img_y = int((y - len(filtro) / 2 + f_y + self.largo) % self.largo)

                        r = self.img_array.item(img_y,img_x,0)
                        g = self.img_array.item(img_y,img_x,1)
                        b = self.img_array.item(img_y,img_x,2)

                        suma_r += r * filtro[f_y][f_x]
                        suma_g += g * filtro[f_y][f_x]
                        suma_b += b * filtro[f_y][f_x]
                    
                new_rgb = (min(max(int(factor * suma_r + brillo), 0), 255),
                           min(max(int(factor * suma_g + brillo), 0), 255),
                           min(max(int(factor * suma_b + brillo), 0), 255))

                self.__modificar_rgb(y,x,new_rgb)

    def filtros_convolucion(self,filtro):
        ''' Funcion que recibe un tipo de filtro de convolución y lo aplica con la matriz
            y valores correspondientes
            
            filtro: str. Filtro seleccionado que se va a aplicar'''

        if filtro == 'Suave':
            self.__aplicar_convolucion(
                [[0.0,0.2,0.0],
                 [0.2,0.2,0.2],
                 [0.0,0.2,0.0]], 1.0, 0.0
            )
        elif filtro == 'Fuerte':
            self.__aplicar_convolucion(
                [[0,0,1,0,0],
                 [0,1,1,1,0],
                 [1,1,1,1,1],
                 [0,1,1,1,0],
                 [0,0,1,0,0]], 1.0 / 13.0, 0.0
            )
        elif filtro == 'Motion Blur':
            self.__aplicar_convolucion(
                [[1, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 1, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 1, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 1, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1]], 1.0 / 9.0, 0.0
            )
        elif filtro == 'Encontrar bordes':
            self.__aplicar_convolucion(
               [[-1,  0, 0,  0,  0],
                [ 0, -2, 0,  0,  0],
                [ 0,  0, 6,  0,  0],
                [ 0,  0, 0, -2,  0],
                [ 0,  0, 0,  0, -1]], 1.0, 0.0
            )
        elif filtro == 'Sharpen':
            self.__aplicar_convolucion(
               [[-1, -1, -1],
                [-1,  9, -1],
                [-1, -1, -1]], 1.0, 0.0
            )
        elif filtro == 'Emboss':
            self.__aplicar_convolucion(
               [[-1, -1, -1, -1, 0],
                [-1, -1, -1,  0, 1],
                [-1, -1,  0,  1, 1],
                [-1,  0,  1,  1, 1],
                [ 0,  1,  1,  1, 1]], 1.0, 128.0
            )
        else:
            raise ValueError("Ese filtro de convolucion no existe!")


                
