import pandas as pd
import numpy as np
import os, sys
import shutil
import xml.etree.cElementTree as et
### Crea carpeta de modulos
carpetaModulos = 'modulos'
if os.path.exists(carpetaModulos):
        shutil.rmtree(carpetaModulos)
        os.makedirs(carpetaModulos)
else:
        os.makedirs(carpetaModulos)

#Funcion para obtener unicos datos de una lista
def unique(list1):
    x = np.array(list1)
    return np.unique(x)

#Funcion que exporta un csv nuevo
def exportarCsv(data,nom,ruta):
    nombreAristas = nom
    datos = data
    datos.to_csv(ruta + nombreAristas + '.csv', sep=';', index = False)
rutamodulos = 'modulos/'

# Creando diccionarios de secciones:
##Importamos datos del xml del curso 
parsedXML = et.parse( "course/course/2019-II.xml")
dfcols = ['section']
sec_xml = pd.DataFrame(columns=dfcols)
for node in parsedXML.getroot():
    name = node.attrib.get('url_name')
    if pd.isna(name):
        continue
    else:
        sec_xml = sec_xml.append(pd.Series([name], index=dfcols), ignore_index = True)
##Creamos el diccionario de secciones
dicsec = dict(zip(sec_xml['section'], range(1, len(sec_xml['section'])+1)))

# Creando diccionario de Subsecciones:
##Importamos datos del xml del curso 
dfcols = ['subsection']
subsec_xml = pd.DataFrame(columns=dfcols)
for sec in sec_xml['section']:
    parsedXML = et.parse( "course/chapter/"+ sec +".xml")
    for node in parsedXML.getroot():
        name = node.attrib.get('url_name')
        if pd.isna(name):
            continue
        else:
            subsec_xml = subsec_xml.append(pd.Series([name], index=dfcols), ignore_index = True)
##Creamos el diccionario de subsecciones
dicsubsec = dict(zip(subsec_xml['subsection'], range(1, len(subsec_xml['subsection'])+1)))


##Lee el csv
datos = pd.read_csv('engagement.csv', sep=';',  error_bad_lines=False)


##Identifica Estudiante

colestudiantes = datos['username'].values
#estudiantes = list(dict.fromkeys(colestudiantes))
estudiantes = unique(colestudiantes)
#Une columnas de fecha y hora y ordena cronologicamente

colstiempo = ["date", "time"]
datos['date']= pd.to_datetime(datos.date)
datos['date']= datos['date'].astype(str) + " "
datos['datetime']= datos[colstiempo].sum(1)
datos.drop(colstiempo, 1)
datos = datos.sort_values('datetime')
datos['type']= datos['name']

## filtrar datos sin nav_content, nav_content_next y nav_content_prev, ademas actualiza estudiantes

datosPrimerNivel = datos[~datos.name.isin(["pause_video","stop_video", "nav_content","nav_content_next","nav_content_prev","nav_content_click","nav_content_tab","Signin",""])]
colestudiantesn = datosPrimerNivel['username'].values
estudiantesn = list(dict.fromkeys(colestudiantesn))
estudiantes = estudiantesn
##Selecciona solamente las columnas username y name(tipo de contenido)

#print(estudiantes)
datosPrimerNivel = datosPrimerNivel[['username', 'name', 'type', 'session', 'section','subsection', 'datetime', 'unit']]


#Asigna una sola variable por tipo de contenido:

datosPrimerNivel['name'] = datosPrimerNivel['name'].replace(['play_video'], 'Video')
datosPrimerNivel['name'] = datosPrimerNivel['name'].replace(['problem_check','problem_graded'], 'Quiz')
datosPrimerNivel['name'] = datosPrimerNivel['name'].replace(['edx.forum.response.created','edx.forum.thread.created','edx.forum.comment.created'], 'Forum')
datosPrimerNivel['type']= datosPrimerNivel['name']
## Temporalmente para Quiz
datosPrimerNivel['unit'].fillna('1', inplace=True)
datosPrimerNivel['unit'] = datosPrimerNivel['unit'].replace(['Null', 'NaN'], '1')
## Temporalmente  para la unidad de los foros

## Crea un array de dataframes, un dataframe por estudiante
data_collection = {}
grafo = {}
columns = ['Source', 'Target', 'Student']
datosA = pd.DataFrame(index=[], columns=columns)

# Function to insert row in the dataframe 
def Insert_row(row_number, df, row_value): 
    # Starting value of upper half 
    start_upper = 0
    # End value of upper half 
    end_upper = row_number 
    # Start value of lower half 
    start_lower = row_number 
    # End value of lower half 
    end_lower = df.shape[0] 
    # Create a list of upper_half index 
    upper_half = range(start_upper, end_upper, 1) 
    # Create a list of lower_half index 
    lower_half = range(start_lower, end_lower, 1) 
    # Increment the value of lower half by 1 
    lower_half = [x.__add__(1) for x in lower_half] 
    # Combine the two lists 
    index_ = upper_half + lower_half 
    # Update the index of the dataframe 
    df.index = index_ 
    # Insert a row at the end 
    df.loc[row_number] = row_value 
    # Sort the index labels 
    df = df.sort_index() 
    # return the dataframe 
    return df 

#####################################
dt = datosPrimerNivel
#[['name','session', 'username']]
#print(dt[['name','unit', 'session']])
df_ss = pd.DataFrame()
for est in range(len(estudiantes)):
    nuevo= pd.DataFrame(datosPrimerNivel[datosPrimerNivel['username'] == estudiantes[est]])
    if nuevo.empty:
        continue
    data_collection[est]= nuevo
    data_collection[est].index = pd.RangeIndex(len(data_collection[est].index))
    numeroFilas = data_collection[est].count()
    ## SESIONES SEPARADAS CASOS ESPECIALES
    ses = data_collection[est]['session'].unique()
    for s in ses:
        df_estud = data_collection[est]
        nuevodf= df_estud[df_estud['session'] == s]
        df_ss = df_ss.append(nuevodf, ignore_index = True)
    

datosPrimerNivel = df_ss
#dftemp = datosPrimerNivel[datosPrimerNivel['username'] == 'e16']
#exportarCsv(dftemp, 'ejeme16', rutamodulos)

for est in range(len(estudiantes)):
    nuevo= pd.DataFrame(datosPrimerNivel[datosPrimerNivel['username'] == estudiantes[est]])
    if nuevo.empty:
        continue
    data_collection[est]= nuevo
    data_collection[est].index = pd.RangeIndex(len(data_collection[est].index))
    numeroFilas = data_collection[est].count()
 
    filasainsertar = []
    ## Agrega un signout al final de cada sesion
    for l in range(1,numeroFilas.session):
        if data_collection[est]['session'].iloc[l] != data_collection[est]['session'].iloc[l-1]:
            filasainsertar.append(l)
    for f in range(0, len(filasainsertar)):
        fi = filasainsertar[f]
        fl = f+ fi
        row_signout = [estudiantes[est], 'Signout', 'Signout', data_collection[est]['session'].iloc[fl-1], data_collection[est]['section'].iloc[fl-1], '', data_collection[est]['datetime'].iloc[fl-1], '']
        data_collection[est] = Insert_row(fl, data_collection[est], row_signout)

    numeroFilas = data_collection[est].count()
    filasainsertar = []
    ## Agrega un Signin al inicio de cada sesion
    for l in range(1,numeroFilas.session):
        if data_collection[est]['session'].iloc[l] != data_collection[est]['session'].iloc[l-1]:
            filasainsertar.append(l)
    for f in range(0, len(filasainsertar)):
        fi = filasainsertar[f]
        fl = f+ fi
        row_signin = [estudiantes[est], 'Signin', 'Signin', data_collection[est]['session'].iloc[fl], data_collection[est]['section'].iloc[fl], '', data_collection[est]['datetime'].iloc[fl], '']
        data_collection[est] = Insert_row(fl, data_collection[est], row_signin)
    
    numeroFilas = data_collection[est].count()
    
    ## Agrega fila signin y signou al inicio y final de cada df del estudiante
    row_signin = [estudiantes[est], 'Signin', 'Signin', data_collection[est]['session'].iloc[0], data_collection[est]['section'].iloc[0], '', data_collection[est]['datetime'].iloc[0], '']
    data_collection[est]= Insert_row(0, data_collection[est], row_signin)
    
    row_signout = [estudiantes[est], 'Signout', 'Signout', data_collection[est]['session'].iloc[numeroFilas.session], data_collection[est]['section'].iloc[numeroFilas.session], '', data_collection[est]['datetime'].iloc[numeroFilas.session], '']
    numeroFilas = data_collection[est].count()
    data_collection[est]= Insert_row(numeroFilas.session, data_collection[est], row_signout)

    numeroFilas = data_collection[est].count()

for est in range(len(estudiantes)):
    #valsecs = pd.DataFrame().append(dicsec)
    #secci = data_collection[est]['section'].tolist()
    #valsecs = valsecs[secci].values[0]
    #valsubsecs = dicsubsec[x] for x in data_collection[est]['subsection'
    #data_collection[est]['name'] = data_collection[est]['name'].astype(str)+""+valsecs+""+data_collection[est]['unit']
    data_collection[est]['name'] = data_collection[est]['name'].astype(str)+"_"+data_collection[est]['subsection'].astype(str)+"_"+data_collection[est]['unit']

dftemp = data_collection[5]
#print(dftemp)
exportarCsv(dftemp, 'ejemsiso', rutamodulos)
#print(dftemp[dftemp['session' == 'ccf96478cd58d9f2c650617acbe6a6af']])
for col in dftemp.columns: 
        print(col)
for est in range(len(estudiantes)):
    numeroFilas = data_collection[est].count()
    ##Se comienza a construir edges y nodes
    source = data_collection[est]['name'][0:numeroFilas.username-1]
    target = data_collection[est]['name'][1:numeroFilas.username]
    section_source = data_collection[est]['section'][0:numeroFilas.username-1]
    section_target = data_collection[est]['section'][1:numeroFilas.username]
    student = data_collection[est]['username'][0:numeroFilas.username-1]
    session = data_collection[est]['session'][0:numeroFilas.username-1]
    datetime = data_collection[est]['datetime'][0:numeroFilas.username-1]
    datos_grafo = list(zip(source, target, section_source, section_target, student, session, datetime)) 
    grafo[est] = pd.DataFrame(datos_grafo, columns = ['Source', 'Target', 'SectionSource', 'SectionTarget','Student', 'Session', 'Datetime'])
    datosA = datosA.append(grafo[est], ignore_index=True)

#print(datosA[['Source', 'Target', 'Session']][datosA['Student'] == 'e173'] )
datosA['Source'] = datosA['Source'].replace(['Signin__'], 'Signin')
datosA['Source'] = datosA['Source'].replace(['Signout__'], 'Signout')
datosA['Target'] = datosA['Target'].replace(['Signin__'], 'Signin')
datosA['Target'] = datosA['Target'].replace(['Signout__'], 'Signout')
exportarCsv(datosA, 'antesdegrafo', rutamodulos)

## Se generan dataframes tipo1 por seccion
modulosConNan = unique(datosPrimerNivel['section'].values)
modulos = np.array([x for x in modulosConNan if str(x) != 'nan'])

columnsMod = ['Source', 'Target', 'SectionSource', 'SectionTarget','Student', 'Session', 'Datetime']
columnsCom = ['Source', 'Target', 'SectionSource', 'SectionTarget','Student', 'Session', 'Datetime', 'Week', 'Step']

datosAmodulos = pd.DataFrame(index=[], columns=columnsMod)
datosCompleto = pd.DataFrame(index=[], columns=columnsCom)
datosAmodulosUnidos = pd.DataFrame(index=[], columns=columnsCom)
weeks = pd.DataFrame(index=[], columns = ['Week'])
steps = pd.DataFrame(index=[], columns = ['Step'])

for lm in range(len(modulos)):
    datosAmodulos = pd.concat([datosA.copy(), weeks, steps], axis=1, )
    numeroDatosA = datosAmodulos.count()
    for lf in range(numeroDatosA.Student):
        if datosAmodulos['SectionSource'].iloc[lf] != modulos[lm] and datosAmodulos['Source'][lf] != 'Signin' and datosAmodulos['Source'][lf] != 'Signout':
            datosAmodulos['Source'][lf] = 'Other'
        if datosAmodulos['SectionTarget'].iloc[lf] != modulos[lm] and datosAmodulos['Target'][lf] != 'Signout' and datosAmodulos['Target'][lf] != 'Signin':
            datosAmodulos['Target'][lf] = 'Other'
        #print(datosAmodulos[['Source', 'Target', 'Session']])
    datosAmodulos['Week']= modulos[lm]

    datosEliminar=[]
    for u in range(numeroDatosA.Source):
    ## Elimina datos no relevantes en este nivel
        if datosAmodulos['Source'].iloc[u] == datosAmodulos['Target'].iloc[u]:
            datosEliminar.append(u)
        if datosAmodulos['Source'].iloc[u] == 'Signout' and datosAmodulos['Target'].iloc[u] == 'Signin':
            datosEliminar.append(u)
        '''if datosAmodulos['Source'].iloc[u] == 'Other' and datosAmodulos['Target'].iloc[u] == 'Other':
            datosEliminar.append(u)
        if datosAmodulos['Source'].iloc[u] == 'play_video' and datosAmodulos['Target'].iloc[u] == 'pause_video':
            datosEliminar.append(u)
        if datosAmodulos['Source'].iloc[u] == 'pause_video' and datosAmodulos['Target'].iloc[u] == 'play_video':
            datosEliminar.append(u)
        if datosAmodulos['Source'].iloc[u] == 'play_video' and datosAmodulos['Target'].iloc[u] == 'play_video':
            datosEliminar.append(u)
        if datosAmodulos['Source'].iloc[u] == 'play_video' and datosAmodulos['Target'].iloc[u] == 'stop_video':
            datosEliminar.append(u)'''
    
    '''datosAmodulos['Source'] = datosAmodulos['Source'].replace(['play_video','pause_video','stop_video'], 'Video')
    datosAmodulos['Target'] = datosAmodulos['Target'].replace(['play_video','pause_video','stop_video'], 'Video')'''
    
    datosAmodulos = datosAmodulos.drop(datosEliminar)
    datosAmodulos.index = pd.RangeIndex(len(datosAmodulos.index))
    
    sesAmodulos = unique(datosAmodulos['Session'].values)
    for sa in range(len(sesAmodulos)):
        dfsession = datosAmodulos[datosAmodulos['Session'] == sesAmodulos[sa]]
        ns = dfsession.count()
        oth = ['Other']
        ## No se toman encuenta grafos donde solo hay signin-other-signout
        if ns.Session == 2 and dfsession.Target.isin(oth).any():
            continue
        for l in range(0, ns.Session):
            dfsession['Step'].iloc[l] = l+1 
        datosCompleto = datosCompleto.append(dfsession, ignore_index=True)

## asignacion de caracteres a nodos
'''datosCompleto['Source'] = datosCompleto['Source'].replace(['Signin','Video','Forum','Quiz', 'Signout', 'Other'],[0, 1, 2, 3, 4, 5])
datosCompleto['Target'] = datosCompleto['Target'].replace(['Signin','Video','Forum','Quiz', 'Signout', 'Other'],[0, 1, 2, 3, 4, 5])'''

datosNodos = pd.DataFrame(index =[], columns = ['id', 'label'])
datosNodos['id'] = np.unique(datosCompleto[['Source', 'Target']].values)
datosNodos['label'] = [x.split('_',2)[0] for x in datosNodos['id']]
exportarCsv(datosNodos, 'nodos', rutamodulos)

datosCompleto = datosCompleto[['Source', 'Target','Step', 'SectionSource', 'SectionTarget', 'Student', 'Session', 'Datetime', 'Week']]

exportarCsv(datosCompleto, 'completo', rutamodulos)



'''def exportarCsvStudent(data, user):
    nombreAristas = 'edges_' + user
    datos = data[data['Student']== user]
    datos = datos[['Source', 'Target', 'Student', 'Session']]
    datos.to_csv(nombreAristas + '.csv', sep=';', index = False)
    #print (datos)

def exportarCsvAllStudent(data,nom):
    nombreAristas = 'edges_all_'+nom
    datos = data
    datos.to_csv(nombreAristas + '.csv', sep=';', index = False)
    #print (datos)


option = int(input("1: Para todos los estuiantes, 0: Para un estudiante "))

if option == 1:
    exportarCsvAllStudent(datosA)
else:
    if option == 0:
        usuario = raw_input('Ingrese el usuario a analizar: ')
        exportarCsvStudent(datosA, usuario)'''

"""for key in data_collection.keys():
    print("\n" +"="*40)
    print(estudiantes[key])
    print("-"*40)
    print(data_collection[key])"""

"""for key in grafo.keys():
    print("\n" +"="*40)
    print(estudiantes[key])
    print("-"*40)
    print(grafo[key])"""
