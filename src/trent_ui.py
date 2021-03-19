import PySimpleGUI as sg
from PIL import Image
from tkinter import Tk
from tkinter.filedialog import askopenfilename,asksaveasfilename
from trent_procesador import PDI


def abrir_imagen():
    ''' Función que despliega el cuadro de dialogo para abrir una imagen'''

    Tk().withdraw()
    imagen_original = askopenfilename()
    return imagen_original


def guardar_imagen():
    ''' Función que despliega el cuadro de dialogo para guardar una imagen'''

    Tk().withdraw()
    ruta_carpeta = asksaveasfilename()
    return ruta_carpeta


# Organización de la barra de opciones
menu_def = [ ['Archivo', ['Abrir', 'Guardar', 'Cerrar']],['Imagen',['Filtros',['Grises',['Tono 1','Tono 2','Tono 3','Tono 4','Tono 5','Tono 6','Tono 7','Tono 8','Tono 9'],'Mosaico'],'Brillo','Deshacer']]]


# Organizacion de los componentes de la interfaz
layout = [
    [sg.Menu(menu_def)],
    [sg.Image(key='ORI-IMG')]
]

# Genera la ventana
window = sg.Window('TRENT v1.0', layout,size = (800,500),element_justification = "center",)

img = None
pdi = None

# Loop para procesar los eventos y obtener los valores de los posibles inputs
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Salir': # if user closes window or clicks cancel
        break
    elif event == 'Abrir':
        ruta = abrir_imagen()
        print(ruta)
        if isinstance(ruta,str) and ruta != '':
            if ruta.endswith((".png", ".jpg", ".jpeg")):
                pdi = PDI(ruta)
                window["ORI-IMG"].update(data = pdi.get_img('o'))
            else:
                sg.popup('Formato de archivo inválido! (solo .png .jpg y .jpeg)',title = 'Error',keep_on_top = True)

    elif event == 'Guardar':
        if pdi != None:
            ruta = guardar_imagen()
            if ruta.endswith((".png", ".jpg", ".jpeg")):
                print(ruta)
                if pdi.guardar(ruta):
                    sg.popup("Guardado correctamente")
                else:
                    sg.popup("Formato de guardado no coincide con el formato nativo de la imagen",title = 'Error',keep_on_top = True)
            else:
                sg.popup("Nombre de archivo inválido",title = 'Error',keep_on_top = True)
        else:
            sg.popup("No se ha abierto ninguna imagen",title = 'Error',keep_on_top = True)


    elif event == 'Cerrar':
        pdi = None
        window["ORI-IMG"].update(data = None)

    elif event in ('Tono 1' , 'Tono 2' , 'Tono 3' , 'Tono 4' , 'Tono 5' , 'Tono 6' , 'Tono 7' , 'Tono 8' , 'Tono 9'):
        print(event)

        if pdi != None:
            pdi.gris(event)
            window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Mosaico':
        if pdi != None:

            layout_m = [
                [sg.Text('No. de columnas'),sg.In(size = (5,1),key = 'num_columnas')],
                [sg.Text('No. de filas'),sg.In(size = (5,1),key = 'num_filas')],
                [sg.Button('Aplicar',key = 'apl-mosaico')]
            ]

            win_mosaico = sg.Window('Tamaño mosaico',layout_m,element_justification = 'center',keep_on_top = True,modal = True,size = (200,100))

            while True:
                event3,values3 = win_mosaico.read()

                if event3 == sg.WIN_CLOSED:
                    break
                elif event3 == 'apl-mosaico':
                    
                    try:
                        v_c = int(values3['num_columnas'])
                        v_f = int(values3['num_filas'])
                    except:
                        sg.popup('Valor ingresado no es un entero',title = 'Error',keep_on_top = True)
                        continue

                    pdi.mosaico(v_c,v_f)
                    window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)
        

    elif event == 'Brillo':

        if pdi != None:
            # Organización de los componentes del widget de brillo
            layout_b = [
                [sg.Slider(range = (-100,100),default_value = 0,orientation = 'horizontal',key = 'v-brillo')],
                [sg.Button('Aplicar',key = 'apl-brillo')]
            ]
            
            win_brillo = sg.Window('Brillo',layout_b,element_justification = 'center',keep_on_top = True,modal = True)

            while True:
                event2,values2 = win_brillo.read()

                if event2 == sg.WIN_CLOSED:
                    break
                elif event2 == 'apl-brillo':
                    v = values2['v-brillo']
                    pdi.modificar_brillo(v)
                    window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)
                
    elif event == 'Deshacer':
        if pdi != None:
            pdi.deshacer_filtro()
            window["ORI-IMG"].update(data = pdi.get_img('o'))
# Se cierra la ventana
window.close()