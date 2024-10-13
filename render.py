import markdown

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
render_markdown("aaa.md", "mi_archivo.html")