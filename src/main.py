import re
import markdown
from llm import start_llm
import io
def render_markdown(markdown_file, output_file):
  """Renderiza un archivo Markdown y guarda el HTML resultante en un archivo.

  Args:
      markdown_file: La ruta del archivo Markdown.
      output_file: La ruta del archivo donde se guardará el HTML.
  """

  with open(markdown_file, 'r') as f:
    markdown_text = f.read()

  html = markdown.markdown(markdown_text)

  with open(output_file, 'w') as f:
    f.write(html)

# Ejemplo de uso:
def eliminar_codigo(archivo):
    """Elimina el código dentro de bloques ```python en un archivo.

    Args:
        archivo (str): Nombre del archivo.
    """
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Encuentra todos los bloques de código
    bloques_codigo = re.findall(r'```python\n(.*?)\n```', contenido, re.DOTALL)
    images = []
    # Reemplaza cada bloque de código por una cadena vacía
    for bloque in bloques_codigo:
        #Verificar por cada linea de codigo so el llm puso una imagen dentro del codigo python
        for linea in bloque.splitlines():
            if linea.startswith('!['):
               images.append(linea)
        bloque.replace('![', '#![')
        exec(bloque)
        contenido = contenido.replace(f'```python\n{bloque}\n```', '\n'.join(images))

    # Escribe el contenido modificado en el archivo
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)

start_llm()
# Llama a la función para eliminar el código
eliminar_codigo('out/informe.md')
render_markdown("out/informe.md", "informe.html")