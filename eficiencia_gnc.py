import sqlite3
import os
import tkinter as tk

os.system('cls')

#  Creando la ventana del resumen de datos
def start_tkinter(texto):
    # Se crea la ventana principal y se establecen sus dimensiones
    total = tk.Tk()
    total.title('Datos principales') # Titulo
    total.geometry('520x260+560+240') # Dimensiones
    
    # Se muestran los datos en la ventana
    x = 0
    for i in texto:
        label = tk.Label(total, text=i, font=("Arial", 15))
        label.grid(row=x, column=0, sticky="w")
        x+=1

    # Se establece una funcion para cerrar la ventana...
    def cerrar_ventana():
        total.destroy()

    # ...entro de este boton
    boton_cerrar = tk.Button(total, text="Cerrar",
                             command=cerrar_ventana, font=("Arial", 15))
    boton_cerrar.grid(row=x+1, column=0, pady=30)

    # Se inicializa la ventana. Aqui termina el programa
    total.mainloop()


gastos_nafta = [8000] # Irrelevante por el momento


# Funcion que procesa todos los datos y da un calculo final
def calcular_costo_total(datos):
    
    distancia_total = sum(datos[etapa]['distancia'] for etapa in datos)
    litros_consumidos = sum(datos[etapa]['litros_consumidos']
                            for etapa in datos)
    costo_total = sum(datos[etapa]['litros_consumidos'] *
                      datos[etapa]['precio_por_litro'] for etapa in datos)
    eficiencia_total = distancia_total / litros_consumidos
    # El consumo que hubiera tenido si hubiese andado a nafta
    costo_Nafta = sum(datos[etapa]['litros_consumidos'] * datos[etapa]['Pr_aprox_NAFTA'] for etapa in datos)

    return {
        'distancia_total': distancia_total,
        'litros_consumidos': litros_consumidos,
        'costo_total': costo_total,
        'eficiencia_total': eficiencia_total,
        'costo_nafta': costo_Nafta, 
        'ahorro': costo_Nafta - costo_total
    }

# Funcion que conecta con la base de datos y obtiene los datos de esta
def obtener_datos_desde_db():
    # Conectarse a la base de datos SQLite
    conexion = sqlite3.connect('eficiencia_gnc.db')
    cursor = conexion.cursor()

    # Ejecutar una consulta para obtener los datos

    cursor.execute("SELECT * FROM Viajes")
    # ejecutar una consulta entre la etapa 6 y la 10
    # min, max = 1, 17
    # cursor.execute(f"SELECT * FROM Viajes WHERE Etapa >= {min} AND Etapa <= {max};")

    datos_desde_db = {}

    # Recorrer los resultados y almacenarlos en el diccionario
    for fila in cursor.fetchall():
        etapa = fila[0]  # Supongamos que la columna 0 es el nombre de la etapa
        datos_desde_db[etapa] = {
            # Supongamos que la columna 1 es la distancia
            'distancia': fila[1],
            # Supongamos que la columna 2 son los litros consumidos
            'litros_consumidos': fila[2],
            # Supongamos que la columna 3 es el precio por metro gnc
            'precio_por_litro': fila[3],
            # Supongamos que la columna 4 es el precio por litro NAFTA
            'Pr_aprox_NAFTA': fila[4]
        }

    # Cerrar la conexión
    conexion.close()

    return datos_desde_db

# Funcion que calcula lo que se gasto, y la eficiencia del coche por cada etapa
def costo_eficiencia_parcial(datos):
    for dato in datos:
        costo_de_etapa = datos[dato]['litros_consumidos'] * \
            datos[dato]['precio_por_litro']
        eficiencia = datos[dato]['distancia'] / \
            datos[dato]['litros_consumidos']
        print(
            f'En la etapa {dato} gastaste: $ {costo_de_etapa:.2f} y la eficiencia fue de {eficiencia:.1f} km/l')

# Funcion que calcula el costo en gas, lo que hubiera sido en nafta, y calcula el ahorro por cada etapa
def costo_ahorro_parcial(datos):
    for dato in datos:
        costo_gas = datos[dato]['litros_consumidos'] * datos[dato]['precio_por_litro']
        costo_nafta = datos[dato]['litros_consumidos'] * datos[dato]['Pr_aprox_NAFTA']
        ahorro = costo_nafta - costo_gas
        print(
            f"En la etapa {dato}: GAS: ${costo_gas:.2f}; NAFTA: ${costo_nafta:.2f}, ahorro: ${ahorro:.2f}")

# Funcion principal
def main():
    # Obtener datos desde la base de datos
    datos_db = obtener_datos_desde_db()

    # Calcular resultados
    resultados = calcular_costo_total(datos_db)

    # Imprimir resultados, estos se muestran en la ventana principal
    distancia = f"La distancia total recorrida es:   {resultados['distancia_total']:.2f} km."
    metros = f"Los metros de gas totales consumidos son:   {resultados['litros_consumidos']:.2f} m3."
    costo_gas = f"El costo total del viaje es:   {resultados['costo_total']:.2f} pesos."
    eficiencia = f"La eficiencia total del viaje es:   {resultados['eficiencia_total']:.2f} km/m3."
    costo_nafta = f"El costo total en NAFTA hubiera sido:   {resultados['costo_nafta']:.2f} pesos."
    ahorro = f"Te ahorraste:   {resultados['ahorro']:.2f} pesos."

    # # # Lo mismo que los datos anteriores, pero en una sola variable
    # resultados = f"""La distancia total recorrida es {resultados['distancia_total']:.2f} km.
    # Los metros de gas totales consumidos son {resultados['litros_consumidos']:.2f} m3.
    # El costo total del viaje es {resultados['costo_total']:.2f} pesos.
    # La eficiencia total del viaje es {resultados['eficiencia_total']:.2f} km/m3.
    # El costo total en NAFTA hubiera sido {resultados['costo_nafta']:.2f} pesos.
    # Te ahorraste {resultados['ahorro']:.2f} pesos.\n"""

    # Una lista con los resultados, para poder mostralo luego en la ventana
    res = [distancia, metros, costo_gas, eficiencia, costo_nafta, ahorro]
    # print(resultados)
    for result in res:
        print(result)
    print('\n')


    # Calcular y mostrar resultados parciales
    costo_eficiencia_parcial(datos_db)
    print()

    costo_ahorro_parcial(datos_db)
    print()

    # Muestra los datos de la DB sin ningun procesado
    for dato in datos_db:
        print(f"Etapa {dato}: " + str(datos_db[dato]))

    # Inicia la funcion de la ventana
    start_tkinter(res)


if __name__ == '__main__':
    # Crear base de datos si no existe
    if not os.path.exists('eficiencia_gnc.db'):
        db = sqlite3.connect('eficiencia_gnc.db')
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Viajes (
                            Etapa INTEGER PRIMARY KEY AUTOINCREMENT,
                            Distancia_recorrida REAL NOT NULL,
                            litros_consumidos REAL NOT NULL,
                            precio_por_litro REAL NOT NULL,
                            Pr_aprox_NAFTA REAL NOT NULL,
                            ahorro INT);'''
                       )
        db.close()
    main()


"""
Con este codigo se crea una base de datos llamada eficiencia_gnc.db que contiene los siguientes campos:
- Etapa (campo clave primaria autoincrementable).
- Distancia recorrida en km.
- Litros consumidos (en realidad metros cubicos de gas).
- Precio por litro (en realidad metro cubico de gas).
- Precio de NAFTA aproximado.
- Ahorro calculado.

El programa no introduce datos, solo consulta y muestra lo que hay en la base de datos.
Para introducir datos se debe hacer manualmente, sugiero el siguiente comando para testear.

INSERT INTO Viajes (Distancia_recorrida, litros_consumidos, precio_por_litro) VALUES
    (43.1, 5.80, 195),
    (98.5, 7.54, 250),
    (73.5, 8.00, 250),
    (75.3, 7.07, 250),
    (55.1, 7.3, 220),
    (61.4, 5.19, 300);


El programa permite introducir los valores para cada campo y luego calcular el ahorro parcial hasta esa etapa.
Se utiliza el modulo tkinter para mostrar la interfaz gráfica y permitir al usuario visualizar los datos mas relevantes.
Se utiliza el modulo sqlite3 para interactuar con la base de datos.

La funcion main() es la encargada de interactuar con el usuario y realizar las operaciones correspondientes con la base de datos.
La funcion main es donde se encuentran las funciones principales del programa.

"""
