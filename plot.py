# String con el código Python para generar el gráfico
codigo_grafico = """
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output.csv")
df["Hora"] = pd.to_datetime(df["Hora"], unit="s")

fig, ax = plt.subplots(figsize=(12, 6))

for columna in df.columns[1:]:
    ax.plot(df["Hora"], df[columna], label=columna)

ax.legend()
ax.set_xlabel("Hora")
ax.set_ylabel("Cantidad")
ax.set_title("Serie de Tiempo de Cantidad de Personas en Diferentes Ubicaciones")

plt.show()
"""

# Ejecutar el código del string
exec(codigo_grafico)