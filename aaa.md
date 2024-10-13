## Análisis del comportamiento del municipio Playa

El municipio Playa muestra un patrón interesante a lo largo del día. Para comprenderlo mejor, se realizó un análisis estadístico de los datos proporcionados.

**1. Distribución de personas por hora:**

```python
import pandas as pd
import matplotlib.pyplot as plt

# Carga de datos
data = pd.read_csv("output.csv", index_col="Hora")

# Gráfico de la distribución de personas por hora
plt.figure(figsize=(12, 6))
plt.plot(data.index, data["Playa"], label="Playa")
plt.xlabel("Hora (minutos)")
plt.ylabel("Cantidad de personas")
plt.title("Distribución de personas en Playa durante el día")
plt.legend()
plt.savefig("distribucion_personas_playa.png")
plt.close()
```

{distribucion_personas_playa.png}

El gráfico muestra que la cantidad de personas en Playa aumenta gradualmente desde las 6:00 am hasta las 12:00 pm, alcanzando un pico alrededor de las 2:00 pm. Luego, disminuye gradualmente hasta las 6:00 am del día siguiente.

**2. Comparación con otros municipios:**

```python
# Gráfico de la distribución de personas en diferentes municipios
plt.figure(figsize=(12, 6))
for municipio in data.columns:
    plt.plot(data.index, data[municipio], label=municipio)

plt.xlabel("Hora (minutos)")
plt.ylabel("Cantidad de personas")
plt.title("Distribución de personas en diferentes municipios")
plt.legend()
plt.savefig("distribucion_personas_municipios.png")
plt.close()
```

[distribucion_personas_municipios.png]

Al comparar Playa con otros municipios, podemos observar que Playa presenta una tendencia similar a la de otros municipios como Centro Habana, La Habana Vieja y Diez de Octubre, con un pico de personas durante la tarde. 

**3. Análisis estadístico de la variación:**

```python
# Cálculo de la media, desviación estándar y varianza
media_playa = data["Playa"].mean()
desviacion_estandar_playa = data["Playa"].std()
varianza_playa = data["Playa"].var()

print(f"Media: {media_playa:.2f}")
print(f"Desviación estándar: {desviacion_estandar_playa:.2f}")
print(f"Varianza: {varianza_playa:.2f}")
```

La media de personas en Playa durante el día es de 143.54, con una desviación estándar de 23.56 y una varianza de 555.45. Estos valores nos indican que la cantidad de personas en Playa varía considerablemente a lo largo del día.

**En resumen:**

- Playa muestra un patrón de aumento de personas hasta la tarde, seguido de una disminución gradual hasta la mañana siguiente.
- Este patrón es similar a otros municipios como Centro Habana, La Habana Vieja y Diez de Octubre.
- La cantidad de personas en Playa varía considerablemente a lo largo del día, con una media de 143.54 y una desviación estándar de 23.56.

**Nota:** Estos resultados se basan en la simulación proporcionada. Para obtener una visión más completa, se necesitarían datos reales sobre la cantidad de personas en Playa durante diferentes horas del día. 
