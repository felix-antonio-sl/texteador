import streamlit as st
import os
from openai import OpenAI

# Inicializar el cliente OpenAI
def initialize_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("API Key de OpenAI no configurada. Verifica la variable de entorno.")
        return None
    return OpenAI(api_key=api_key)

def main():
    # Inicializar cliente de OpenAI
    openai_client = initialize_openai_client()
    if not openai_client:
        return

    # Título de la aplicación
    st.title("Refactorización de Árboles de Contenido")

    # Descripción de la aplicación
    st.write("Esta aplicación toma uno o más árboles de contenido, una finalidad específica y especificaciones adicionales para generar un árbol refactorizado.")

    # Entrada del usuario: Árboles de contenido
    arboles_input = st.text_area("Introduce los árboles de contenido (en formato JSON o texto estructurado):")

    # Entrada del usuario: Finalidad
    finalidad_input = st.text_input("Finalidad específica:")

    # Entrada del usuario: Especificaciones
    especificaciones_input = st.text_area("Especificaciones adicionales (en formato texto o JSON):")

    # Botón para generar el árbol refactorizado
    if st.button("Generar Árbol Refactorizado"):
        if arboles_input and finalidad_input and especificaciones_input:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[
                        {"role": "system", "content": "Eres un asistente experto en la organización y estructuración de contenidos..."},
                        {"role": "user", "content": f"""
### Instructions:

1. Analyze Content:
   - Step 1: Review content trees. Understand hierarchy and key elements.
   - Step 2: Summarize structure. Focus on main elements. Identify patterns.

2. Filter by Purpose:
   - Step 1: Identify elements aligned with the purpose.
   - Step 2: Apply specifications. Exclude non-compliant elements. Briefly justify exclusions.

3. Restructure:
   - Step 1: Organize selected elements according to purpose.
   - Step 2: Merge, split, or reorder elements for coherence and effectiveness.

4. Build New Content Tree:
   - Step 1: Present the new tree in Spanish. Ensure clear, logical hierarchy.
   - Step 2: Structure each level to support the purpose. Maximize alignment with specifications.

5. Expand Details:
   - Step 1: Detail each line of the restructured tree. Break down to the atomic level (smallest unit).

6. Review and Refine:
   - Step 1: Check tree for completeness and coherence.
   - Step 2: Get feedback on internal consistency. Adjust as needed.
   - Step 3: Perform final review. Correct errors and inconsistencies.

Output Format:
- Hierarchical content tree with uppercase titles for top levels, sublevels as bullet points.
- Include a brief summary of significant changes per section.

Inputs:
- Content Trees: <trees>{arboles_input}</trees>
- Purpose: <purpose>{finalidad_input}</purpose>
- Specifications: <specs>{especificaciones_input}</specs>
                    """}
                    ]
                )
                # Mostrar el árbol refactorizado en un text area
                st.subheader("Árbol Refactorizado:")
                st.text_area("Resultado", response.choices[0].message.content, height=300)
            except Exception as e:
                st.error(f"Error al llamar a la API de OpenAI: {e}")
        else:
            st.warning("Por favor, completa todos los campos antes de generar el árbol refactorizado.")

if __name__ == "__main__":
    main()
