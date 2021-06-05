import PySimpleGUI as sg
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
menu_def = [['Archivo', ['Abrir', 'Guardar', 'Cerrar']],
            ['Imagen',['Filtros',
                        ['Grises',['Tono 1','Tono 2','Tono 3','Tono 4','Tono 5','Tono 6','Tono 7','Tono 8','Tono 9'],
                        'Mosaico',
                        'Alto contraste',
                        'Inverso',
                        'Componentes RGB',
                        'Blur',['Suave','Fuerte'],
                        'Motion Blur',
                        'Encontrar bordes',
                        'Sharpen',
                        'Emboss'],
                    'Convertir a letras',
                    'Brillo',
                    'Deshacer']]]

#

# Organizacion de los componentes de la interfaz
layout = [
    [sg.Menu(menu_def)],
    [sg.Image(key='ORI-IMG')]
]

# Genera la ventana
window = sg.Window('TRENT v2.0', layout,size = (800,500),element_justification = "center",)

img = None
pdi = None

# Loop para procesar los eventos y obtener los valores de los posibles inputs
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Salir': # if user closes window or clicks cancel
        break
    
    elif event == 'Abrir':

        ruta = abrir_imagen()

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

        if pdi != None:
            pdi.gris(int(event[-1]))
            window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Mosaico':

        if pdi != None:
            # Organización de los componentes del widget de brillo
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

    elif event == 'Alto contraste':
    
        if pdi != None:
            pdi.alto_contraste()
            window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Inverso':
        
        if pdi != None:
            pdi.inverso()
            window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Componentes RGB':
    
        if pdi != None:
            # Organización de los componentes del widget de componentes RGB
            layout_rgb = [
                [sg.Text('Rojo: '),sg.Slider(range = (0,100),default_value = 0,orientation = 'horizontal',key = 'v-rojo')],
                [sg.Text('Verde: '),sg.Slider(range = (0,100),default_value = 0,orientation = 'horizontal',key = 'v-verde')],
                [sg.Text('Azul: '),sg.Slider(range = (0,100),default_value = 0,orientation = 'horizontal',key = 'v-azul')],
                [sg.Button('Aplicar',key = 'apl-rgb')]
            ]
            
            win_rgb = sg.Window('Componentes RGB',layout_rgb,element_justification = 'center',keep_on_top = True,modal = True)

            while True:
                event_rgb,val_rgb = win_rgb.read()

                if event_rgb == sg.WIN_CLOSED:
                    break
                elif event_rgb == 'apl-rgb':
                    n_r = int(val_rgb['v-rojo'])
                    n_g = int(val_rgb['v-verde'])
                    n_b = int(val_rgb['v-azul'])

                    pdi.capa_rgb(n_r,n_g,n_b)
                    window["ORI-IMG"].update(data = pdi.get_img('m'))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event in ('Suave','Fuerte','Motion Blur','Encontrar bordes','Sharpen','Emboss'):
        
        if pdi != None:
            pdi.filtros_convolucion(event)
            window["ORI-IMG"].update(data = pdi.get_img('m'))

    elif event == 'Convertir a letras':
        if pdi != None:

            layout_letras = [
                [sg.Text('Selecciona una de las opciones:')],
                [sg.Radio('Solo letra M',"R-LETRAS",key='m-cl')],
                [sg.Radio('Solo letra M con tono gris',"R-LETRAS",key='m-g')],
                [sg.Radio('16 letras simulando 256 tonos',"R-LETRAS",key='ds-t')],
                [sg.Radio('16 letras con tono gris',"R-LETRAS",key='ds-g')],
                [sg.Radio('Texto personalizado',"R-LETRAS",key='tp-cl')],
                [sg.Radio('Fichas de domino blancas',"R-LETRAS",key='db')],
                [sg.Radio('Fichas de domino negras',"R-LETRAS",key='dn')],
                [sg.Radio('Fichas con naipes',"R-LETRAS",key='nps')],
                [sg.Button('Continuar',key='ctn-letras')]
            ]

            win_text = sg.Window('Convertir a letras',layout_letras,element_justification = 'left',keep_on_top = True,modal = True)

            while True:
                event_letras,val_letras = win_text.read()

                opciones = ['m-cl','m-g','ds-t','ds-g','tp-cl','db','dn','nps']

                if event_letras == sg.WIN_CLOSED:
                    break

                elif event_letras == 'ctn-letras':

                    for i in range(0,len(opciones)):
                        if win_text[opciones[i]].get():
                            layout_cdr = [
                                [sg.Text('No. de columnas'),sg.In(size = (5,1),key = 'num_columnas')],
                                [sg.Text('No. de filas'),sg.In(size = (5,1),key = 'num_filas')],
                                [sg.Button('Aplicar',key = 'apl-cdr')]
                            ]

                            win_cdr = sg.Window('Tamaño mosaico',layout_cdr,element_justification = 'center',keep_on_top = True,modal = True,size = (200,100))

                            while True:
                                event_cdr,values_cdr = win_cdr.read()

                                if event_cdr == sg.WIN_CLOSED:
                                    break
                                elif event_cdr == 'apl-cdr':
                                    try:
                                        v_c = int(values_cdr['num_columnas'])
                                        v_f = int(values_cdr['num_filas'])
                                    except:
                                        sg.popup('Valor ingresado no es un entero',title = 'Error',keep_on_top = True)
                                        continue

                                    pdi.filtros_letras(v_c,v_f,opciones[i])
                                    window["ORI-IMG"].update(data = pdi.get_img('m'))
                                    win_cdr.close()
                                    win_text.close()
                                    sg.popup_no_buttons('¡Proceso finalizado!',title = 'TRENT',auto_close = True,auto_close_duration = 3,keep_on_top = True)
                            break
                    
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)
                
    elif event == 'Deshacer':

        if pdi != None:
            pdi.deshacer_filtro()
            window["ORI-IMG"].update(data = pdi.get_img('o'))

# Se cierra la ventana
window.close()