import sqlite3
import os
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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


# gastos_nafta = [8000, 10000, 10000, 15000, 13905, 15000, 16035, 30000, 30000]  # Irrelevante por el momento
# litros_nafta = [10.1, 11.85, 10.88, 17.24, 15, 15.94, 15, 26.32, 25.38] # Irrelevante por el momento


# Funcion que procesa todos los datos y da un calculo final
def calcular_costo_total(datos):
    # Convertimos los valores en arrays de NumPy para cálculos más rápidos
    distancias = np.array([datos[etapa]['Distancia_recorrida'] for etapa in datos])
    litros = np.array([datos[etapa]['litros_consumidos'] for etapa in datos])
    precios_gnc = np.array([datos[etapa]['precio_por_litro'] for etapa in datos])
    precios_nafta = np.array([datos[etapa]['Pr_aprox_NAFTA'] for etapa in datos])

    distancia_total = distancias.sum()
    litros_consumidos = litros.sum()
    costo_total = (litros * precios_gnc).sum()
    eficiencia_total = distancia_total / litros_consumidos
    costo_nafta = (litros * precios_nafta).sum()
    ahorro = costo_nafta - costo_total

    return {
        'distancia_total': distancia_total,
        'litros_consumidos': litros_consumidos,
        'costo_total': costo_total,
        'eficiencia_total': eficiencia_total,
        'costo_nafta': costo_nafta,
        'ahorro': ahorro
    }

# Funcion que conecta con la base de datos y obtiene los datos de esta
def obtener_datos_desde_db():
    # Conectarse a la base de datos y leer los datos directamente en un DataFrame
    conexion = sqlite3.connect('./base_prueba.db')
    df = pd.read_sql_query("SELECT * FROM Viajes", conexion)
    conexion.close()

    # Convertir el DataFrame en un diccionario de listas (manteniendo compatibilidad con tu código)
    datos_desde_db = df.set_index("Etapa").to_dict(orient="index")
    return datos_desde_db

# Funcion que calcula lo que se gasto, y la eficiencia del coche por cada etapa
def costo_eficiencia_parcial(datos):
    for dato in datos:
        costo_de_etapa = datos[dato]['litros_consumidos'] * datos[dato]['precio_por_litro']
        eficiencia = datos[dato]['Distancia_recorrida'] / datos[dato]['litros_consumidos']
        print(f'En la etapa {dato} gastaste: $ {costo_de_etapa:.2f} y la eficiencia fue de {eficiencia:.1f} km/l')

# Funcion que calcula el costo en gas, lo que hubiera sido en nafta, y calcula el ahorro por cada etapa
def costo_ahorro_parcial(datos):
    for dato in datos:
        costo_gas = datos[dato]['litros_consumidos'] * datos[dato]['precio_por_litro']
        costo_nafta = datos[dato]['litros_consumidos'] * datos[dato]['Pr_aprox_NAFTA']
        ahorro = costo_nafta - costo_gas
        print(
            f"En la etapa {dato}: GAS: ${costo_gas:.2f}; NAFTA: ${costo_nafta:.2f}, ahorro: ${ahorro:.2f}")

# Funcion que grafica
def graficar_eficiencia_y_ahorro(datos):
    etapas = np.array(list(datos.keys()))
    eficiencia = np.array([datos[e]['Distancia_recorrida'] / datos[e]['litros_consumidos'] for e in etapas])
    costos_gnc = np.array([datos[e]['litros_consumidos'] * datos[e]['precio_por_litro'] for e in etapas])
    costos_nafta = np.array([datos[e]['litros_consumidos'] * datos[e]['Pr_aprox_NAFTA'] for e in etapas])

    # Calcular porcentaje de ahorro
    ahorro_porcentaje = np.where(costos_nafta > 0, (costos_nafta - costos_gnc) / costos_nafta * 100, 0)

    # Seleccionar 10 puntos equidistantes
    num_puntos = 10
    indices = np.linspace(0, len(etapas) - 1, num_puntos, dtype=int)

    etapas_mostradas = etapas[indices]
    eficiencia_mostrada = eficiencia[indices]
    ahorro_mostrado = ahorro_porcentaje[indices]

    plt.figure(figsize=(10,5))

    # Gráfico de eficiencia
    plt.subplot(1,2,1)
    plt.plot(etapas_mostradas, eficiencia_mostrada, marker='o', linestyle='-', color='blue', alpha=0.7)
    plt.xlabel("Etapas seleccionadas")
    plt.ylabel("Eficiencia (km/m³)")
    plt.title("Eficiencia del GNC en 10 etapas representativas")

    # Gráfico de porcentaje de ahorro
    plt.subplot(1,2,2)
    plt.plot(etapas_mostradas, ahorro_mostrado, marker='o', linestyle='-', color='green', alpha=0.7)
    plt.xlabel("Etapas seleccionadas")
    plt.ylabel("Ahorro (%)")
    plt.title("Porcentaje de ahorro en 10 etapas representativas")

    plt.tight_layout()
    plt.show()

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

    graficar_eficiencia_y_ahorro(datos_db)

    # Inicia la funcion de la ventana
    start_tkinter(res)


if __name__ == '__main__':
    # Crear base de datos si no existe
    if not os.path.exists('./base_prueba.db'):
        db = sqlite3.connect('./base_prueba.db')
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
