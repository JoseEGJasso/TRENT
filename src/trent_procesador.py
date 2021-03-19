from PIL import Image
from io import BytesIO as io


class PDI(object):
    ''' Clase que se encarga de la lógica de cada uno de los filtros y modificaciones'''

    def __init__(self, ruta):
        ''' Carga la imagen de acuerdo a la ruta 

            ruta: str. Ruta de la imagen '''

        self.img_o = Image.open(ruta)     # Imagen original
        self.img_m = self.img_o.copy()    # Imagen modificada
        self.ancho = self.img_o.size[0]   # Número de pixeles a lo ancho de la imagen original
        self.largo = self.img_o.size[1]   # Número de pixeles a lo largo de la imagen original


    def __aplicar_filtro(self,ec):
        ''' Función que recibe una ecuación en forma de lambda para ser aplicada
            a todos los pixeles de la imagen

            ec: function. Lambda a aplicar'''

        self.deshacer_filtro()

        for i in range(0,self.ancho):
            for j in range(0,self.largo):

                r = self.img_m.getpixel((i,j))[0]
                g = self.img_m.getpixel((i,j))[1]
                b = self.img_m.getpixel((i,j))[2]

                value = ec(r,g,b)

                print((i,j))

                self.img_m.putpixel((i,j),(value,value,value))


    def deshacer_filtro(self):
        ''' Función que deshace los cambios realizados a la imagen'''

        self.img_m = self.img_o.copy()


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

        self.deshacer_filtro()

        for i in range(0,self.ancho):
            for j in range(0,self.largo):

                r = self.img_m.getpixel((i,j))[0]
                g = self.img_m.getpixel((i,j))[1]
                b = self.img_m.getpixel((i,j))[2]

                n_r = 0 if (r+cons) < 0 else 255 if (r+cons) > 255 else int(r+cons)
                n_g = 0 if (g+cons) < 0 else 255 if (g+cons) > 255 else int(g+cons)
                n_b = 0 if (b+cons) < 0 else 255 if (b+cons) > 255 else int(b+cons)

                self.img_m.putpixel((i,j),(n_r,n_g,n_b))


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
            aux = self.img_m.copy()

        return self.__resize_img(aux,700,700)


    def guardar(self,ruta):
        ''' Función que guarda la imagen modificada en la ruta ingresada.
        
            Regresa True si se realizó el guardadi exitosmente
            Regresa False si el formato no coincidió
            
            ruta: str. Ruta donde se va a guardar la imagen'''

        if self.img_o.format == 'PNG':
            if ruta.endswith('.png'):
                self.img_m.save(ruta,format = self.img_o.format)
                return True

        elif self.img_o.format == 'JPEG':
            if ruta.endswith((".jpg",".jpeg")):
                self.img_m.save(ruta, format = self.img_m.format)
                return True

        elif self.img_o.format == None:
            self.img_m.save(ruta)
            return True

        return False


    def mosaico(self,num_columnas,num_filas):
        '''Función que aplica el filtro de mosaico a la imagen

            num_columnas: int. Ancho del mosaico
            num_filas: int. Largo del mosaico '''

        self.deshacer_filtro()

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
                        print((c,f))
                        self.img_m.putpixel((c,f),new_rgb)
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

                r = self.img_m.getpixel((i,j))[0] 
                g = self.img_m.getpixel((i,j))[1] 
                b = self.img_m.getpixel((i,j))[2] 

                total_r += r
                total_g += g
                total_b += b

        return (total_r // total_pixeles,total_g // total_pixeles,total_b // total_pixeles)