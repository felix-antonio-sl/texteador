import streamlit as st
import openai
import os
from io import StringIO

# Función para inicializar el cliente de OpenAI
def initialize_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("API Key de OpenAI no configurada. Verifica la variable de entorno.")
        return None
    return openai.OpenAI(api_key=api_key)

# Cargar contenido desde uno o varios archivos o desde una entrada de texto
def load_content(files=None, text_input=None, placeholder="", height=200):
    content = ""
    if files:
        for file in files:
            if file is not None:
                content += StringIO(file.getvalue().decode("utf-8")).read() + "\n"
    elif text_input:
        content = text_input
    else:
        content = st.text_area(placeholder, height=height)
    return content

# Función para generar el prompt para el modelo de OpenAI
def create_prompt(tree_structure, text_source):
    return f"""
### Instructions: Generate a Structured Text

Mission: Reconstruct a detailed text using only the 'content tree' and 'source text'. Do not add or omit information. The text must match the structure of the content tree and be complete.

Inputs:
- Content tree: `<tree>{tree_structure}</tree>`
- Source text: `<source>{text_source}</source>`

Steps:

1. Identify Hierarchy:
   - Analyze the 'content tree'. Reflect the hierarchy using markdown:
     - `#` for main titles
     - `##` for subtitles
     - `###`, `####`, etc., for sublevels

2. Extract Content:
   - Match each line of the tree with the source text.
   - Extract all relevant information for each line. Include every detail.
   - For each line, reconstruct the most exhaustive and detailed text possible. Do not summarize.
   - If no information is found, note: "Insufficient information in the source text".

3. Reconstruct Text:
   - Write a detailed and exhaustive text for each line of the tree using the extracted content.
   - Ensure coherence and avoid repetition.

4. Review:
   - Confirm that the final text covers all points from the content tree and source text.
   - Use markdown for formatting.
   - The text must be in Spanish.

Important: The final text must be exhaustive, detailed, and faithful to the source. Each line must be treated with maximum depth.
"""

# Función para realizar la reconstrucción del texto utilizando OpenAI
def reconstruct_text(client, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # Ajustar al modelo adecuado
            messages=[
                {"role": "system", "content": "Eres un asistente de IA que ayuda a reconstruir textos."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=16383,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al reconstruir el texto: {e}")
        return None

# Página principal para la reconstrucción de textos
def main():
    st.title("Reconstructor de Texto")
    
    # Inicializar cliente de OpenAI
    client = initialize_openai_client()
    if not client:
        return
    
    # Opción de carga del árbol de contenidos
    tree_input_option = st.radio("¿Cómo deseas ingresar la estructura del árbol?", ("Subir archivo", "Escribir manualmente"))

    if tree_input_option == "Subir archivo":
        tree_file = st.file_uploader("Sube el archivo con el Árbol de Contenidos", type=["txt"])
        tree_structure = load_content(files=[tree_file])
    else:
        tree_structure = st.text_area("Introduce la estructura del árbol aquí...", height=200)

    # Cargar textos fuente (pueden ser múltiples archivos)
    text_files = st.file_uploader("Sube los archivos con el Texto Fuente (puedes subir múltiples archivos)", type=["txt"], accept_multiple_files=True)
    text_source = load_content(files=text_files, placeholder="Introduce el texto fuente aquí...")

    # Botón para iniciar la reconstrucción del texto
    if st.button("Reconstruir Texto"):
        with st.spinner("Trabajando en la reconstrucción del texto..."):
            prompt = create_prompt(tree_structure, text_source)
            reconstructed_text = reconstruct_text(client, prompt)
            
            if reconstructed_text:
                st.markdown("### Texto Reconstruido")
                st.markdown(reconstructed_text)
                
                st.download_button(
                    label="Descargar Texto Reconstruido",
                    data=reconstructed_text.encode('utf-8'),
                    file_name="texto_reconstruido.txt",
                    mime="text/plain"
                )

# Nota: El bloque if __name__ == "__main__": no es necesario en este archivo.
