import streamlit as st
import os
import fitz  # PyMuPDF para manejo de PDFs
from docx import Document
import markdown
from openai import OpenAI

# Inicializar el cliente OpenAI
openai_client = OpenAI()

# Configurar la clave API de OpenAI desde las variables de entorno
openai_client.api_key = os.getenv("OPENAI_API_KEY")

def generar_prompt_descomposicion(texto, arbol_referencial=None):
    if arbol_referencial:
        prompt = f"""
## Task: Deepening the Provided Hierarchical Content Tree

### Important Instructions:

1. Start from the Provided Tree:
   - Use the given reference tree as the foundation.
   - Do not alter the initial structure of the tree.
   - Only deepen the hierarchy further by breaking down the content into more granular, atomic units.

2. Deepen Each Branch:
   - Expand each branch of the provided tree by decomposing the text down to the most detailed level possible.
   - The goal is to reach the atomic units of information for each segment of the tree.

3. Line-by-Line Analysis:
   - Perform the analysis on a line-by-line basis, ensuring that each line is fully broken down to the atomic level before moving to the next.
   - Continue deepening until you reach the maximum level of detail possible.

4. Output in Spanish:
   - Ensure that all outputs, including titles, subtitles, and atomic units, are written in Spanish.

### Reference Content Tree:
{arbol_referencial}

### Example of Expected Output:

Given the following tree:
```
- Título General
  - Título Principal 1
    - Subtítulo 1.1
```

Expand it as follows:
```
- Título General
  - Título Principal 1
    - Subtítulo 1.1
      - Unidad Atómica 1.1.1
      - Unidad Atómica 1.1.2
      - Unidad Atómica 1.1.3
  - Título Principal 2
    - Subtítulo 2.1
      - Unidad Atómica 2.1.1
      - Unidad Atómica 2.1.2
```

### Text to Decompose:
<cont>{texto}</cont>

### Execute:
- Decompose the text provided by deepening the reference tree down to the atomic level for each branch.
"""
    else:
        prompt = f"""
## Task: Recursive Hierarchical Decomposition of Text

### Steps:

1. Analyze the Text:
   - Read the text between `<cont>` tags. Ensure complete understanding.

2. Define General Title:
   - Create a clear, concise title that encapsulates the entire text.

3. Perform Hierarchical Decomposition:
   - Main Titles: Identify and define the main sections.
   - Subtitles: Break down each main title into precise subtitles.
   - Atomic Units: Further decompose each subtitle down to the most granular, atomic level. Ensure every line reaches this level.

4. Structure the Hierarchy:
   - Use dashes (`-`) to represent each level of the hierarchy.
   - Indent properly to reflect subordination.
   - Ensure each level is consistently detailed. Each title and subtitle must be fully broken down to atomic units.

5. Line-by-Line Analysis:
   - Perform the analysis on a line-by-line basis, ensuring that each line is fully broken down to the atomic level before moving to the next.
   - Continue deepening until you reach the maximum level of detail possible.

6. Output in Spanish:
   - Ensure that all outputs, including titles, subtitles, and atomic units, are written in Spanish.

### Guidelines:

- Be Concise: Titles and subtitles must be short, descriptive, and devoid of redundancy.
- Consistency: Maintain uniform detail across all levels.
- Classify Unclear Content: Any ambiguous sections go under "Others."
- Exclude Irrelevant Information: Disregard non-essential elements like metadata or side notes.

### Example of Expected Output:
```
- Título General
  - Título Principal 1
    - Subtítulo 1.1
      - Unidad Atómica 1.1.1
      - Unidad Atómica 1.1.2
  - Título Principal 2
    - Subtítulo 2.1
      - Unidad Atómica 2.1.1
```

### Text to Decompose:
<cont>{texto}</cont>
"""
    return prompt

def procesar_texto_con_openai(texto, arbol_referencial=None):
    try:
        prompt = generar_prompt_descomposicion(texto, arbol_referencial)
        response = openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Eres un asistente de IA para análisis de texto y estructuración de contenido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=16000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al procesar el texto con OpenAI: {str(e)}")
        return ""

def leer_pdf(archivo_pdf):
    try:
        bytes_pdf = archivo_pdf.read()
        doc = fitz.open(stream=bytes_pdf, filetype="pdf")
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        return texto
    except Exception as e:
        st.error(f"Error al leer el archivo PDF: {str(e)}")
        return ""

def leer_docx(archivo_docx):
    try:
        doc = Document(archivo_docx)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        st.error(f"Error al leer el archivo DOCX: {str(e)}")
        return ""

def leer_markdown(archivo_md):
    try:
        texto_md = archivo_md.read().decode("utf-8")
        return markdown.markdown(texto_md)
    except Exception as e:
        st.error(f"Error al leer el archivo Markdown: {str(e)}")
        return ""

def main():
    st.title("Descomponedor de Contenidos")
    st.write("Ingresa un texto o sube un archivo de texto para su descomposición jerárquica recursiva.")

    # Entrada de texto manual
    texto_ingresado = st.text_area("Ingresa el texto aquí:")

    # Opción para subir un archivo de texto
    archivo_subido = st.file_uploader("O sube un archivo de texto", type=["txt", "pdf", "docx", "md"])

    # Entrada opcional del árbol referencial
    arbol_referencial = st.text_area("Ingresa el árbol de contenidos referencial (opcional):")

    texto_a_procesar = ""

    # Verifica si el usuario ingresó texto manualmente o subió un archivo
    if texto_ingresado:
        texto_a_procesar = texto_ingresado
    elif archivo_subido:
        if archivo_subido.type == "application/pdf":
            texto_a_procesar = leer_pdf(archivo_subido)
        elif archivo_subido.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            texto_a_procesar = leer_docx(archivo_subido)
        elif archivo_subido.type == "text/markdown":
            texto_a_procesar = leer_markdown(archivo_subido)
        else:
            try:
                texto_a_procesar = archivo_subido.getvalue().decode("utf-8")
            except Exception as e:
                st.error(f"Error al leer el archivo de texto: {str(e)}")

    # Botón para procesar el texto
    if st.button("Procesar Texto"):
        if texto_a_procesar:
            with st.spinner("Procesando..."):
                resultado = procesar_texto_con_openai(texto_a_procesar, arbol_referencial)
            if resultado:
                st.success("Texto procesado exitosamente!")
                st.text_area("Resultado:", value=resultado, height=300)
        else:
            st.error("Por favor, ingresa un texto o sube un archivo para continuar.")

if __name__ == "__main__":
    main()