# app.py

import streamlit as st
import Concis  # Página 1: Traductor a Español Conciso
import Descom  # Página 2: Descomposición de Contenidos
import Recon   # Página 3: Reconstrucción de Texto
import Refac  # Página 4: Refactorización de Árboles de Contenido

# Configuración de la barra lateral
st.sidebar.title("Utilidades")
st.sidebar.markdown("### Selecciona una herramienta:")
seleccion = st.sidebar.radio("", ["Concisión", "Descomposición", "Reconstrucción", "Refactorización"])

# Navegación entre las aplicaciones/páginas
if seleccion == "Concisión":
    Concis.main()  # Llamar a la función principal de la primera página
elif seleccion == "Descomposición":
    Descom.main()  # Llamar a la función principal de la segunda página
elif seleccion == "Reconstrucción":
    Recon.main()  # Llamar a la función principal de la tercera página
elif seleccion == "Refactorización":
    Refac.main()  # Llamar a la función principal de la cuarta página
