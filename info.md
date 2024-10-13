## Análisis estadístico de la cantidad de personas en municipios de La Habana

Este análisis utilizará el conjunto de datos CSV proporcionado para realizar un análisis estadístico de la cantidad de personas en diferentes municipios de La Habana durante un período de simulación. Se utilizará la biblioteca Pandas de Python para manipular los datos y matplotlib para la visualización.

**1. Carga de datos y exploración inicial**

Primero, cargamos los datos en un DataFrame de Pandas y realizamos una exploración inicial:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output.csv")

# Mostrar las primeras filas del DataFrame
print(df.head())

# Obtener información básica sobre el DataFrame
print(df.info())

# Calcular estadísticas descriptivas básicas
print(df.describe())
```
 Este código primero importa las bibliotecas necesarias. Luego, lee el archivo CSV en un DataFrame de pandas. Se asume que el archivo CSV se llama "datos_habana.csv".

A continuación, se imprimen las primeras filas del DataFrame usando `df.head()`. Esto proporciona una visión general de la estructura de los datos.

Se utiliza `df.info()` para obtener información básica sobre el DataFrame, como el número de filas y columnas, los tipos de datos de las columnas y el uso de memoria.

Finalmente, `df.describe()` calcula estadísticas descriptivas básicas para cada columna numérica del DataFrame, como el conteo, la media, la desviación estándar, el mínimo, los percentiles y el máximo.

**2. Análisis de Tendencias:**

```python
# Graficar la evolución de la cantidad de personas en cada municipio a lo largo del tiempo
plt.figure(figsize=(12, 6))
for municipio in df.columns[1:]:
    plt.plot(df["Hora"], df[municipio], label=municipio)
plt.xlabel("Hora")
plt.ylabel("Cantidad de Personas")
plt.title("Evolución de la Cantidad de Personas por Municipio")
plt.legend(loc="upper left", bbox_to_anchor=(1,1))
plt.show()
```
 Este código crea un gráfico de líneas que muestra la evolución de la cantidad de personas en cada municipio a lo largo del tiempo. El gráfico tendrá un tamaño de 12x6 pulgadas. Se itera sobre cada columna del DataFrame (excepto la columna "Hora") y se traza la columna "Hora" en el eje x y el valor de la columna actual en el eje y. Se agrega una etiqueta al gráfico para cada municipio. Finalmente, se muestra el gráfico con etiquetas para el eje x, el eje y y un título.

**3. Análisis de Distribución:**

```python
# Crear histogramas para visualizar la distribución de la cantidad de personas en cada municipio
df.hist(figsize=(15,10))
plt.tight_layout()
plt.show()
```

Este código crea histogramas para cada columna numérica (que representan los municipios) en el DataFrame. Los histogramas son útiles para visualizar la distribución de los datos.

**4. Correlaciones:**

```python
# Calcular la matriz de correlación entre municipios
correlation_matrix = df.corr()
print(correlation_matrix)

# Visualizar la matriz de correlación usando un mapa de calor
plt.figure(figsize=(10, 8))
plt.imshow(correlation_matrix, cmap="coolwarm", interpolation="nearest")
plt.colorbar()
plt.xticks(range(len(df.columns)), df.columns, rotation=90)
plt.yticks(range(len(df.columns)), df.columns)
plt.title("Matriz de Correlación entre Municipios")
plt.show()
```

Este código primero calcula la matriz de correlación entre todas las columnas del DataFrame utilizando el método `corr()`. La matriz de correlación muestra la correlación lineal entre cada par de columnas. Un valor cercano a 1 indica una fuerte correlación positiva, un valor cercano a -1 indica una fuerte correlación negativa y un valor cercano a 0 indica una correlación débil o nula.

A continuación, se utiliza `plt.imshow()` para crear un mapa de calor de la matriz de correlación. Un mapa de calor es una representación gráfica de datos donde los valores se representan mediante colores. En este caso, los colores más cálidos representan correlaciones más fuertes, mientras que los colores más fríos representan correlaciones más débiles.

Se agregan etiquetas a los ejes x e y del mapa de calor utilizando `plt.xticks()` y `plt.yticks()`. Las etiquetas se rotan 90 grados para facilitar la lectura.

Finalmente, se agrega un título al mapa de calor utilizando `plt.title()`.

**5. Conclusiones Preliminares:**

Basado en los resultados de este análisis inicial, se pueden obtener algunas conclusiones preliminares sobre la cantidad de personas en los diferentes municipios de La Habana. Sin embargo, se necesita un análisis más profundo y la interpretación en el contexto del estudio de simulación para obtener conclusiones más precisas. 

**Recomendaciones:**

* **Análisis de series temporales:** dado que los datos se recopilaron a lo largo del tiempo, sería beneficioso aplicar técnicas de análisis de series temporales para identificar patrones y tendencias a lo largo del tiempo.
* **Comparaciones entre municipios:** realizar comparaciones más detalladas entre los municipios, incluyendo pruebas estadísticas para determinar si existen diferencias significativas en la cantidad de personas.
* **Análisis de factores externos:** considerar la posibilidad de incorporar factores externos, como eventos especiales o condiciones climáticas, que puedan influir en la cantidad de personas en cada municipio.

Al realizar análisis adicionales y considerar el contexto de la simulación, se puede obtener una comprensión más completa de la dinámica de la población en los diferentes municipios de La Habana.
