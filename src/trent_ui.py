import PySimpleGUI as sg

from tkinter import Tk
from tkinter.filedialog import askopenfilename,asksaveasfilename

from trent_procesador import PDI
from matplotlib.font_manager import fontManager


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


def seleccionador_fuente():

    dict_fonts = {}

    for f in fontManager.ttflist:
        dict_fonts[f.name] = f.fname

    nombres = list(dict_fonts.keys())

    nombres.sort()

    col_op = [
        [sg.Text('Opacidad:',justification = 'left')],
        [sg.Slider(key = 'sld-op',range = (0,100),default_value = 50,orientation = 'h',size = (16,None))]
    ]

    layout_font = [
        [sg.Listbox(nombres,[nombres[0]],key = 'l-fonts',size = (20,10),enable_events = True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE'),
         sg.Listbox([i for i in range(6,31)],default_values = [6],key = 'sz-font',size = (4,10),select_mode = 'LISTBOX_SELECT_MODE_SINGLE', enable_events = True),
         sg.Column(col_op,size = (None,200)) ],
        [sg.Text('Abcd',size = (310,None),auto_size_text = False,key = 'example-txt',text_color = '#000000',background_color = 'white',justification = 'center')],
        [sg.Button('Aplicar',key = 'apl-font')]
    ]

    win_fnt = sg.Window('Selecciona fuente de texto',layout_font,modal = True,auto_size_text = False,size = (400,360),element_justification = 'center')

    while True:
        event_fnt,values_fnt = win_fnt.read()

        estilo = ""
        font_out = None

        if event_fnt in ['l-fonts','sz-font','apl-font']:

            familia = values_fnt['l-fonts'][0]
            tamanio = values_fnt['sz-font'][0]

            font_ruta = dict_fonts[familia]

            win_fnt['example-txt'].update(font = (familia,tamanio))

            if event_fnt == 'apl-font':
                alpha = values_fnt['sld-op']
                font_out = (font_ruta,tamanio,alpha)
                win_fnt.close()
                return font_out

        elif event_fnt == sg.WIN_CLOSED:
            win_fnt.close()
            return font_out


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
                    'Marca de agua',
                    'Convertir a imagen recursiva',['Tonos de gris','Color'],
                    'Brillo',
                    'Deshacer']]]


# Organizacion de los componentes de la interfaz
layout = [
    [sg.Menu(menu_def)],
    [sg.Image(key='ORI-IMG',size = (700,400))],
    #[sg.Text('Tamaño: 2348x1093',size = (800,1),justification = 'center')],
    #[sg.Button('Ver imagen',size = (None,1))]
]

# Genera la ventana
window = sg.Window('TRENT v2.2',layout,size = (800,500),element_justification = "center",auto_size_text = False)

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
            if ruta.lower().endswith((".png", ".jpg", ".jpeg")):
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
            pdi.gris(int(event[-1]),True)
            window["ORI-IMG"].update(data = pdi.get_img('m',True))
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
                    window["ORI-IMG"].update(data = pdi.get_img('m',True))
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
                    pdi.modificar_brillo(v,True,False)
                    window["ORI-IMG"].update(data = pdi.get_img('m',True))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Alto contraste':
    
        if pdi != None:
            pdi.alto_contraste(True)
            window["ORI-IMG"].update(data = pdi.get_img('m',True))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Inverso':
        
        if pdi != None:
            pdi.inverso(True)
            window["ORI-IMG"].update(data = pdi.get_img('m',True))
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

                    pdi.capa_rgb(n_r,n_g,n_b,True,True)
                    window["ORI-IMG"].update(data = pdi.get_img('m',True))
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event in ('Suave','Fuerte','Motion Blur','Encontrar bordes','Sharpen','Emboss'):
        
        if pdi != None:
            pdi.filtros_convolucion(event)
            window["ORI-IMG"].update(data = pdi.get_img('m',True))

    elif event == 'Convertir a letras':
        if pdi != None:

            layout_letras = [
                [sg.Text('Selecciona una de las opciones:')],
                [sg.Radio('Solo letra M',"R-LETRAS",key='m-cl')],
                [sg.Radio('Solo letra M con tono gris',"R-LETRAS",key='m-g')],
                [sg.Radio('16 letras simulando 256 tonos',"R-LETRAS",key='ds-t')],
                [sg.Radio('16 letras simulando 256 tonos a color',"R-LETRAS",key='ds-c')],
                [sg.Radio('16 letras con tono gris',"R-LETRAS",key='ds-g')],
                [sg.Radio('Texto personalizado',"R-LETRAS",key='tp-cl')],
                [sg.Radio('Fichas de domino blancas',"R-LETRAS",key='db')],
                [sg.Radio('Fichas de domino negras',"R-LETRAS",key='dn')],
                [sg.Radio('Fichas con naipes',"R-LETRAS",key='nps')],
                [sg.Button('Continuar',key='ctn-letras')]
            ]

            win_letras = sg.Window('Convertir a letras',layout_letras,element_justification = 'left',keep_on_top = True,modal = True)

            while True:
                event_letras,val_letras = win_letras.read()

                opciones = ['m-cl','m-g','ds-t','ds-c','ds-g','tp-cl','db','dn','nps']

                if event_letras == sg.WIN_CLOSED:
                    break

                elif event_letras == 'ctn-letras':
                    
                    txt = None
                    cerrar = False

                    for i in range(0,len(opciones)):
                        if win_letras[opciones[i]].get():

                            if opciones[i] == 'tp-cl':
                                layout_txt = [
                                    [sg.Text('Ingresa el texto que deseas poner en la imagen:')],
                                    [sg.Input(size=(60,5), key = 'input-txt')],
                                    [sg.Button('Continuar', key = 'ctn-txt')]
                                ]

                                win_txt = sg.Window('Ingresa el texto',layout_txt,element_justification = 'left',keep_on_top = True,modal = True)

                                while True:

                                    event_txt,values_txt = win_txt.read()

                                    cerrar = False

                                    if event_txt == sg.WIN_CLOSED:
                                        cerrar = True
                                        break
                                    
                                    elif event_txt == 'ctn-txt':
                                        txt = values_txt['input-txt']
                                        if txt == '':
                                            sg.popup('Ingresa un texto! >:(',title = 'Error',keep_on_top = True)
                                            continue
                                        break

                            if cerrar:
                                break

                            if opciones[i] in ['db','dn']:
                                info = 'Se recomienda el tamaño 12x12'
                            elif opciones[i] == 'nps':
                                info = 'Se recomienda el tamaño 11x13'
                            else:
                                info = 'Se recomienda el tamaño 8x8'

                            layout_cdr = [
                                [sg.Text(info,key='txt-recom')],
                                [sg.Text('No. de columnas'),sg.In(size = (5,1),key = 'num_columnas')],
                                [sg.Text('No. de filas'),sg.In(size = (5,1),key = 'num_filas')],
                                [sg.Button('Aplicar',key = 'apl-cdr')]
                            ]

                            win_cdr = sg.Window('Tamaño cuadricula',layout_cdr,element_justification = 'center',keep_on_top = True,modal = True,size = (222,130))

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
                                        
                                    win_cdr.hide()
                                    win_letras.hide()

                                    pdi.filtros_letras(v_c,v_f,opciones[i],txt)
                                    window["ORI-IMG"].update(data = pdi.get_img('m',True))

                                    win_cdr.close()
                                    win_letras.close()

                                    if opciones[i] == 'tp-cl':
                                        win_txt.close()

                                    sg.popup_no_buttons('¡Proceso finalizado!',title = 'TRENT',no_titlebar = True,auto_close = True,auto_close_duration = 3,keep_on_top = True)
                            break
                    
        else:
            sg.popup('No se ha abierto ninguna imagen',title = 'Error',keep_on_top = True)

    elif event == 'Marca de agua':

        txt_ma = ""
        cerrar_ma = False

        if pdi != None:
            layout_ma = [
                [sg.Text('Ingresa el texto que deseas poner de marca de agua:')],
                [sg.Input(size=(60,5), key = 'input-ma')],
                [sg.Button('Continuar', key = 'ctn-ma')]
            ]

            win_ma = sg.Window('Marca de agua',layout_ma,element_justification = 'left',keep_on_top = True,modal = True)

            while True:

                event_ma,values_ma = win_ma.read()

                cerrar_ma = False

                if event_ma == sg.WIN_CLOSED:
                    cerrar_ma = True
                    break
                
                elif event_ma == 'ctn-ma':
                    txt_ma = values_ma['input-ma']
                    if txt_ma == '':
                        sg.popup('Ingresa un texto! >:(',title = 'Error',keep_on_top = True)
                        continue
                    win_ma.hide()
                    break
            
            if cerrar_ma:
                win_ma.close()
                continue

            layout_coords = [
                [sg.Text('Selecciona las coordenadas de la imagen donde \n quieres que se genere la marca de agua:')],
                [sg.Text('Coordenada en x'),sg.In(size = (7,1),key = 'coord-x')],
                [sg.Text('Coordenada en y'),sg.In(size = (7,1),key = 'coord-y')],
                [sg.Button('Continuar',key = 'ctn-ma')]
            ]

            win_coords = sg.Window('Selecciona coordenadas',layout_coords,element_justification = 'left',keep_on_top = True,modal = True,size = (315,150))

            while True:
                event_coords,values_coords = win_coords.read()

                cerrar_ma = False

                if event_coords == sg.WIN_CLOSED:
                    cerrar_ma = True
                    break

                elif event_coords == 'ctn-ma':
                    
                    try:
                        v_x = int(values_coords['coord-x'])
                        v_y = int(values_coords['coord-y'])

                        ancho = pdi.get_tamanio()[0]
                        alto = pdi.get_tamanio()[1]

                        if v_x <= 0 or v_x >= ancho or v_y <= 0 or v_y >= alto:
                            sg.popup('Los valores ingresados no son validos',title = 'Error',keep_on_top = True)    
                            continue

                    except:
                        sg.popup('Valor ingresado no es un entero',title = 'Error',keep_on_top = True)
                        continue
                    win_coords.hide()
                    break
            
            if cerrar_ma:
                win_coords.close()
                continue

            f = seleccionador_fuente()

            if f == None:
                sg.popup('No se ha seleccionado ninguna fuente!',title = 'Error',keep_on_top = True)
                continue

            pdi.marca_de_agua(txt_ma,f,v_x,v_y)

            window["ORI-IMG"].update(data = pdi.get_img('m',False))

            sg.popup_no_buttons('¡Proceso finalizado!',title = 'TRENT',no_titlebar = True,auto_close = True,auto_close_duration = 3,keep_on_top = True)

            win_ma.close()
            win_coords.close()

    elif event in ['Tonos de gris','Color']:

        img_ancho,img_alto = pdi.get_tamanio()

        ancho_default = 10 if (img_ancho / 500) < 1 else int((img_ancho / 500) * 10)
        alto_default = 10 if (img_ancho / 500) < 1 else int((img_alto / 500) * 10)

        col_default = 10 if (img_ancho / 500) < 1 else int((img_ancho / 500) * 10)
        fil_default = 10 if (img_alto / 500) < 1 else int((img_alto / 500) * 10)

        no_aplicar = False

        if pdi != None:
            columna_tmn = [
                [sg.Text('Tamaño imagen recursiva',justification = 'center')],
                [sg.Text('Ancho:'),sg.In(str(ancho_default),size = (5,1),key = 'ancho_img_rcsv')],
                [sg.Text('Alto:   '),sg.In(str(alto_default),size = (5,1),key = 'alto_img_rcsv')]
            ]

            columna_cuad = [
                [sg.Text('Tamaño de la cuadricula',justification = 'center')],
                [sg.Text('No. de columnas:'),sg.In(str(col_default),size = (5,1),key = 'num_columnas')],
                [sg.Text('No. de filas:        '),sg.In(str(fil_default),size = (5,1),key = 'num_filas')]
            ]

            layout_rcsv = [
                [sg.Text('Se calcularon los valores recomendados')],
                [sg.Column(columna_tmn,size = (180,100),element_justification = 'center',vertical_alignment = 'center'),sg.VSeparator('black'),
                sg.Column(columna_cuad,size = (180,100),element_justification = 'center',vertical_alignment = 'center')],
                [sg.Button('Aplicar',key = 'apl-rcsv',pad = ((1,1),(1,1)))]
            ]

            win_rcsv = sg.Window('Selecciona tamaño',layout_rcsv,size = (410,185),modal = True,element_justification = 'center')

            while True:
                event_rcsv,values_rcsv = win_rcsv.read()

                if event_rcsv == sg.WIN_CLOSED:
                    no_aplicar = True
                    break            

                elif event_rcsv == 'apl-rcsv':
                    try:
                        v_ancho = int(values_rcsv['ancho_img_rcsv'])
                        v_alto = int(values_rcsv['alto_img_rcsv'])
                        v_c = int(values_rcsv['num_columnas'])
                        v_f = int(values_rcsv['num_filas'])

                        ancho = pdi.get_tamanio()[0]
                        alto = pdi.get_tamanio()[1]

                        if v_c <= 0 or v_c >= ancho or v_f <= 0 or v_f >= alto:
                            sg.popup('Los valores ingresados no son validos',title = 'Error',keep_on_top = True)    
                            continue
                    except:
                        sg.popup('Valor ingresado no es un entero',title = 'Error',keep_on_top = True)
                        continue

                    win_rcsv.hide()
                    break

            if no_aplicar:
                win_rcsv.close()
                continue

            if event == 'Tonos de gris':
                pdi.aplica_img_recursiva(True, v_ancho, v_alto, v_c, v_f)
            else:
                pdi.aplica_img_recursiva(False, v_ancho, v_alto, v_c, v_f)

            window["ORI-IMG"].update(data = pdi.get_img('m',True))

            win_rcsv.close()

    elif event == 'Deshacer':

        if pdi != None:
            pdi.deshacer_filtro()
            window["ORI-IMG"].update(data = pdi.get_img('o'))

# Se cierra la ventana
window.close()