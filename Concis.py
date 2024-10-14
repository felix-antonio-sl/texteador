import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
from docx import Document
import fitz  # PyMuPDF

# Inicializar el cliente de OpenAI
def initialize_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Función para dividir el texto en fragmentos manejables
def split_text_into_chunks(text, max_chars=5000):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            potential_end = text.rfind('\n', start, end)
            if potential_end == -1:
                potential_end = text.rfind('. ', start, end)
            if potential_end != -1:
                end = potential_end + 1  # Incluir el punto y espacio en el corte
        chunks.append(text[start:end].strip())
        start = end
    return chunks

# Función para traducir un fragmento de texto a español conciso usando la API de OpenAI
@st.cache_data  # Uso de cache_data para almacenar resultados serializables
def translate_chunk_to_concise_spanish(_client, chunk, model):
    prompt = (
        "You are an assistant specialized in translating text into concise Spanish. "
        "Translate the following text into Spanish, preserving the informational integrity with the minimum possible characters. "
        "Do not omit key details, especially in lists. Reduce words without summarizing. Use abbreviations when possible, without losing clarity. "
        "Do not use bold or other emphasis formats. Omit metadata, links, and references. "
        "The text to be translated is: {chunk}"
    )
    
    response = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.format(chunk=chunk)}
        ],
        temperature=0,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    return f"<©>{response.choices[0].message.content.strip()}</©>"

# Función para traducir un fragmento de texto a inglés conciso usando la API de OpenAI
@st.cache_data  # Uso de cache_data para almacenar resultados serializables
def translate_chunk_to_concise_english(_client, chunk, model):
    prompt = (
        "You are an assistant specialized in translating text into concise English. "
        "Translate the following text into English, preserving the informational integrity with the minimum possible characters. "
        "Do not omit key details, especially in lists. Reduce words without summarizing. Use abbreviations when possible, without losing clarity. "
        "Do not use bold or other emphasis formats. Omit metadata, links, and references. "
        "The text to be translated is: {chunk}"
    )
    
    response = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.format(chunk=chunk)}
        ],
        temperature=0,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    return f"<©>{response.choices[0].message.content.strip()}</©>"

# Función para procesar el texto completo
def process_text(_client, text, model, chunk_size, language):
    chunks = split_text_into_chunks(text, max_chars=chunk_size)
    st.write(f"El texto se ha dividido en {len(chunks)} fragmentos.")
    
    translation = ""
    for i, chunk in enumerate(chunks):
        st.write(f"Procesando fragmento {i + 1} con el modelo {model}...")
        if language == "Español Conciso":
            translated_chunk = translate_chunk_to_concise_spanish(_client, chunk, model)
        else:
            translated_chunk = translate_chunk_to_concise_english(_client, chunk, model)
        translation += translated_chunk + "\n\n"
    
    return translation

# Función para leer archivos .docx
def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Función para leer archivos .md
def read_md(file):
    return file.read().decode('utf-8')

# Función para leer archivos PDF
def read_pdf(file):
    pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_reader)):
        page = pdf_reader.load_page(page_num)
        text += page.get_text()
    return text

# Función para generar el nombre del archivo con los detalles adicionales
def generate_filename(base_name, model, chunk_size, language):
    date_str = datetime.now().strftime("%Y%m%d")
    chunk_str = f"_{chunk_size // 1000}k" if chunk_size >= 1000 else f"_{chunk_size}"
    lang_str = "es_conciso" if language == "Español Conciso" else "en_conciso"
    return f"{base_name}_{lang_str}_{date_str}_{model}{chunk_str}.txt"

# Página principal para la traducción
def main():
    st.title("Traductor Conciso")
    st.write("Sube un documento de texto o ingresa el texto directamente para traducirlo a una versión concisa en el idioma seleccionado.")
    
    client = initialize_openai_client()
    
    # Selección del idioma
    language_option = st.selectbox(
        "Selecciona el idioma para la traducción:",
        ("Español Conciso", "Inglés Conciso")
    )
    
    # Selección del modelo
    model_option = st.selectbox(
        "Selecciona el modelo para la traducción:",
        ("gpt-4o-mini", "gpt-4o-2024-08-06")
    )
    
    # Selección del tamaño de los fragmentos
    chunk_size = st.selectbox(
        "Selecciona el tamaño de los fragmentos de texto (en caracteres):",
        (5000, 10000, 15000),
        index=0  # 5000 caracteres por defecto
    )
    
    # Opción 1: Subir archivo
    uploaded_file = st.file_uploader("Sube tu archivo de texto", type=["txt", "doc", "docx", "md", "pdf"])
    
    # Opción 2: Ingresar texto directamente
    user_text = st.text_area("O ingresa el texto a traducir")
    
    if uploaded_file:
        # Leer el texto del archivo según su tipo
        text = ""
        if uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode('utf-8')
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        elif uploaded_file.type == "text/markdown" or uploaded_file.name.endswith(".md"):
            text = read_md(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        else:
            st.error("Tipo de archivo no soportado.")
            return
        
        # Verificar si ya existe una traducción en el estado de la sesión
        cache_key = f"{uploaded_file.name}_{language_option}"
        if 'concise_translation' not in st.session_state or st.session_state.get('file_name') != cache_key:
            st.session_state['concise_translation'] = process_text(client, text, model_option, chunk_size, language_option)
            st.session_state['file_name'] = cache_key
        
        # Mostrar la traducción completa
        if language_option == "Español Conciso":
            st.header("Traducción Completa en Español Conciso")
        else:
            st.header("Complete Translation in Concise English")
        st.text_area("Traducción", st.session_state['concise_translation'], height=300)
    
        # Generar el nombre del archivo de descarga con los detalles adicionales
        translated_file_name = generate_filename(os.path.splitext(uploaded_file.name)[0], model_option, chunk_size, language_option)
    
        # Botón para descargar la traducción
        st.download_button("Descargar Traducción", st.session_state['concise_translation'].encode('utf-8'), translated_file_name)
    
    elif user_text:
        # Procesar el texto ingresado manualmente
        cache_key = "manual_input_" + language_option
        if 'concise_translation' not in st.session_state or st.session_state.get('file_name') != cache_key:
            st.session_state['concise_translation'] = process_text(client, user_text, model_option, chunk_size, language_option)
            st.session_state['file_name'] = cache_key
        
        # Mostrar la traducción completa
        if language_option == "Español Conciso":
            st.header("Traducción Completa en Español Conciso")
        else:
            st.header("Complete Translation in Concise English")
        st.text_area("Traducción", st.session_state['concise_translation'], height=300)
    
        # Generar el nombre del archivo de descarga con los detalles adicionales
        translated_file_name = generate_filename("traducción_concisa" if language_option == "Español Conciso" else "concise_translation", model_option, chunk_size, language_option)
    
        # Botón para descargar la traducción
        st.download_button("Descargar Traducción", st.session_state['concise_translation'].encode('utf-8'), translated_file_name)

if __name__ == "__main__":
    main()
