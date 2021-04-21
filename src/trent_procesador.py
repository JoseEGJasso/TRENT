from PIL import Image
import io
import os
import numpy as np


class PDI(object):

    def __init__(self, ruta):

        self.img_o = Image.open(ruta)
        self.img_m = self.img_o.copy()
        self.columns = self.img_o.size[0]
        self.rows = self.img_o.size[1]

        print(self.img_o.size)

    def __aplicar_filtro(self,ec):
        
        self.deshacer_filtro()

        for i in range(0,self.columns):
            for j in range(0,self.rows):

                r = self.img_m.getpixel((i,j))[0]
                g = self.img_m.getpixel((i,j))[1]
                b = self.img_m.getpixel((i,j))[2]

                value = ec(r,g,b)

                print((i,j))

                self.img_m.putpixel((i,j),(value,value,value))


    def deshacer_filtro(self):

        self.img_m = self.img_o.copy()


    def gris(self,tono):

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

        self.deshacer_filtro()

        for i in range(0,self.columns):
            for j in range(0,self.rows):

                r = self.img_m.getpixel((i,j))[0]
                g = self.img_m.getpixel((i,j))[1]
                b = self.img_m.getpixel((i,j))[2]

                n_r = 0 if (r+cons) < 0 else 255 if (r+cons) > 255 else int(r+cons)
                n_g = 0 if (g+cons) < 0 else 255 if (g+cons) > 255 else int(g+cons)
                n_b = 0 if (b+cons) < 0 else 255 if (b+cons) > 255 else int(b+cons)

                self.img_m.putpixel((i,j),(n_r,n_g,n_b))


    def __resize_img(self,aux,heightNew,widthNew):
    
        w,h = aux.size

        while w > 720 or h > 450:
            scale = min(heightNew/h, widthNew/w)
            aux = aux.resize((int(w*scale),int(h*scale)),Image.ANTIALIAS)
            heightNew -= 100
            widthNew -= 100
            w,h = aux.size

        bio = io.BytesIO()
        aux.save(bio,format = "PNG")
        return bio.getvalue()


    def get_img(self,type_img):

        if type_img == 'o':
            aux = self.img_o.copy()
        elif type_img == 'm':
            aux = self.img_m.copy()

        return self.__resize_img(aux,700,700)


    def guardar(self,ruta):
        print(self.img_o.format)

        if self.img_o.format == 'PNG':
            if ruta.endswith('.png'):
                self.img_m.save(ruta,format = self.img_o.format)
                return True
            else:
                return False

        elif self.img_o.format == 'JPEG':
            if ruta.endswith((".jpg",".jpeg")):
                self.img_m.save(ruta, format = self.img_m.format)
                return True
            else:
                return False
        elif self.img_o.format == None:
            self.img_m.save(ruta)
            return True
        else:
            return False


    def mosaico(self,num_columnas,num_filas):

        self.deshacer_filtro()

        for j in range(0,self.rows,num_filas):
            for i in range(0,self.columns,num_columnas):    

                if (i + num_columnas > self.columns) and (j + num_filas > self.rows):
                    new_rgb = self.__color_promedio(i,j,self.columns,self.rows)

                elif (i + num_columnas > self.columns):
                    new_rgb = self.__color_promedio(i,j,self.columns,j+num_filas)

                elif (j + num_filas > self.rows):
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,self.rows)

                else:
                    new_rgb = self.__color_promedio(i,j,i+num_columnas,j+num_filas)

                c = i

                while (c < i + num_columnas) and (c < self.columns):
                    f = j
                    while (f < j + num_filas) and (f < self.rows):
                        print((c,f))
                        self.img_m.putpixel((c,f),new_rgb)
                        f += 1
                    c += 1

        

    def __color_promedio(self,columna_ini,fila_ini,columna_fin,fila_fin):
        
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