import pandas as pd
import numpy as np
##Lee el csv
datos = pd.read_csv('engagement.csv', sep=';',  error_bad_lines=False)

##Identifica Estudiante

colestudiantes = datos['username'].values
estudiantes = list(dict.fromkeys(colestudiantes))
print(estudiantes)
#Une columnas de fecha y hora y ordena cronologicamente

colstiempo = ["date", "time"]
datos['date']= pd.to_datetime(datos.date)
datos['date']= datos['date'].astype(str) + " "
datos['datetime']= datos[colstiempo].sum(1)
datos.drop(colstiempo, 1)
datos = datos.sort_values('datetime')

## filtrar datos sin nav_content, nav_content_next y nav_content_prev, ademas actualiza estudiantes

datosPrimerNivel = datos[~datos.name.isin(["nav_content","nav_content_next","nav_content_prev","nav_content_click","nav_content_tab","Signin",""])]
colestudiantesn = datosPrimerNivel['username'].values
estudiantesn = list(dict.fromkeys(colestudiantesn))
estudiantes = estudiantesn

##Selecciona solamente las columnas username y name(tipo de contenido)

datosPrimerNivel = datosPrimerNivel[['username', 'name', 'session', 'section']]

#Asigna una sola variable por tipo de contenido:

datosPrimerNivel['name'] = datosPrimerNivel['name'].replace(['problem_check','problem_graded'], 'Quiz')
datosPrimerNivel['name'] = datosPrimerNivel['name'].replace(['edx.forum.response.created','edx.forum.thread.created','edx.forum.comment.created'], 'Forum')

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


for est in range(len(estudiantes)):
    nuevo= pd.DataFrame(datosPrimerNivel[datosPrimerNivel['username'] == estudiantes[est]])
    if nuevo.empty:
        continue
    data_collection[est]= nuevo
    data_collection[est].index = pd.RangeIndex(len(data_collection[est].index))
    numeroFilas = data_collection[est].count()
    
    ## Agrega un signout al final de cada sesion
    for l in range(1,numeroFilas.session):
        if data_collection[est]['session'].iloc[l] != data_collection[est]['session'].iloc[l-1]:
            row_signout = [estudiantes[est], 'Signout', data_collection[est]['session'].iloc[l], data_collection[est]['section'].iloc[l]]
            data_collection[est]= Insert_row(l, data_collection[est], row_signout)
        numeroFilas = data_collection[est].count()
    for l in range(1,numeroFilas.session):
        if data_collection[est]['name'].iloc[l] == 'Signout':
            data_collection[est]['session'].iloc[l] = data_collection[est]['session'].iloc[l-1]
    
    ## Agrega un Signin al inicio de cada sesion
    for l in range(1,numeroFilas.session):
        if data_collection[est]['session'].iloc[l] != data_collection[est]['session'].iloc[l-1]:
            row_signin = [estudiantes[est], 'Signin', data_collection[est]['session'].iloc[l], data_collection[est]['section'].iloc[l]]
            data_collection[est]= Insert_row(l, data_collection[est], row_signin)
        numeroFilas = data_collection[est].count()

    #row_signini = [estudiantes[est], 'Signin', data_collection[est]['session'].iloc[0], data_collection[est]['section'].iloc[0]]
    #row_signfin = [estudiantes[est], 'Signout', data_collection[est]['session'].iloc[numeroFilas.session-1]]
    #data_collection[est]= Insert_row(0, data_collection[est], row_signini)
    #data_collection[est]= Insert_row(numeroFilas.session+1, data_collection[est], row_signfin)
    numeroFilas = data_collection[est].count()
    

## Se focaliza en un modulo 1d7d5a6b311445069d3cfc4dd0821b98
for est in range(len(estudiantes)):
    numeroFilas = data_collection[est].count()
    for l in range(numeroFilas.username):
        if data_collection[est]['section'].iloc[l] != 'df13b37d70964faf88cfb44b7a36ac55':
            data_collection[est]['name'].iloc[l] += '_' + str(data_collection[est]['section'].iloc[l])
    
    ## alias para Otro en todos los contenidos + Otro
    for l in range(numeroFilas.username):
        if data_collection[est]['section'].iloc[l] != 'df13b37d70964faf88cfb44b7a36ac55':
            data_collection[est]['name'] = data_collection[est]['name'].replace([data_collection[est]['name'].iloc[l]], 'Other')
    
    colsesion = data_collection[est]['session'].values
    sesiones = list(dict.fromkeys(colsesion))
    
    ##Se comienza a construir edges y nodes
    st1 = data_collection[est]['name'][0:numeroFilas.username-1]
    st2 = data_collection[est]['name'][1:numeroFilas.username]
    student = data_collection[est]['username'][0:numeroFilas.username-1]
    session = data_collection[est]['session'][0:numeroFilas.username-1]
    datos_grafo = list(zip(st1, st2, student, session)) 
    grafo[est] = pd.DataFrame(datos_grafo, columns = ['Source', 'Target', 'Student', 'Session'])
    datosA = datosA.append(grafo[est], ignore_index=True)

print(datosA[datosA['Student']== 'e173'])
## Elimina datos
datosEliminar=[]
numeroDatosA = datosA.count()
lon = numeroDatosA.Source
for u in range(lon):
    if datosA['Source'].iloc[u] == 'Signout' and datosA['Target'].iloc[u] == 'Signin':
        datosEliminar.append(u)
    if datosA['Source'].iloc[u] == 'Other' and datosA['Target'].iloc[u] == 'Other':
        datosEliminar.append(u)
    if datosA['Source'].iloc[u] == 'play_video' and datosA['Target'].iloc[u] == 'pause_video':
        datosEliminar.append(u)
    if datosA['Source'].iloc[u] == 'pause_video' and datosA['Target'].iloc[u] == 'play_video':
        datosEliminar.append(u)
    if datosA['Source'].iloc[u] == 'play_video' and datosA['Target'].iloc[u] == 'play_video':
        datosEliminar.append(u)
    if datosA['Source'].iloc[u] == 'play_video' and datosA['Target'].iloc[u] == 'stop_video':
        datosEliminar.append(u)
    
datosA['Source'] = datosA['Source'].replace(['play_video','pause_video','stop_video'], 'Video')
datosA['Target'] = datosA['Target'].replace(['play_video','pause_video','stop_video'], 'Video')
     
datosA = datosA.drop(datosEliminar)
datosA.index = pd.RangeIndex(len(datosA.index))

## asignacion de caracteres a nodos
datosA['Source'] = datosA['Source'].replace(['Signin','Video','Forum','Quiz', 'Signout', 'Other'],[0, 1, 2, 3, 4, 5])
datosA['Target'] = datosA['Target'].replace(['Signin','Video','Forum','Quiz', 'Signout', 'Other'],[0, 1, 2, 3, 4, 5])

def exportarCsvStudent(data, user):
    nombreAristas = 'edges_' + user
    datos = data[data['Student']== user]
    datos = datos[['Source', 'Target', 'Student', 'Session']]
    datos.to_csv(nombreAristas + '.csv', sep=';', index = False)
    #print (datos)

def exportarCsvAllStudent(data):
    nombreAristas = 'edges_all'
    datos = data[['Source', 'Target']]
    datos.to_csv(nombreAristas + '.csv', sep=';', index = False)
    print (datos)


option = int(input("1: Para todos los estuiantes, 0: Para un estudiante "))

if option == 1:
    exportarCsvAllStudent(datosA)
else:
    if option == 0:
        usuario = raw_input('Ingrese el usuario a analizar: ')
        exportarCsvStudent(datosA, usuario)

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
