import pandas as pd
import streamlit as st
import unicodedata
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from io import BytesIO


def remove_accents(text: str) -> str:
    """Remove accents and diacritics from text for comparison."""
    if not text:
        return ""
    # Normalize to decomposed form (NFD), then remove combining characters
    normalized = unicodedata.normalize('NFD', text)
    return ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')


def normalize_text(text) -> str:
    """Normalize text for comparison (lowercase, strip whitespace, remove accents)."""
    if pd.isna(text) or text == "":
        return ""
    text = str(text).lower().strip()
    return remove_accents(text)


def check_match(autores_list: List[Dict[str, str]], inscriptos_data: List[Dict[str, str]]) -> Tuple[bool, str, Optional[str]]:
    """
    Check if any author from autores_list matches any person in inscriptos_data.
    Returns (matched, confidence_level, matched_author_name)

    Confidence levels (in priority order):
    - "Alta (apellido, nombre, email)" - all three match
    - "Media (apellido, nombre)" - lastName and firstName match
    - "Baja (solo apellido)" - only lastName matches
    - "Sin coincidencia" - no match found
    """
    if not autores_list:
        return False, "Sin coincidencia", None

    best_match = None  # (confidence_priority, confidence_label, author_name)

    for autor in autores_list:
        autor_name = f"{autor['firstName']} {autor['lastName']}".strip()

        for inscripto in inscriptos_data:
            # Check lastName match first (required for any match)
            if not autor['lastName'] or autor['lastName'] != inscripto['lastName']:
                continue

            # Determine confidence level based on what matches
            if (autor['firstName'] and autor['email'] and
                autor['firstName'] == inscripto['firstName'] and
                autor['email'] == inscripto['email']):
                # High confidence - return immediately
                return True, "Alta (apellido, nombre, email)", autor_name

            elif (autor['firstName'] and
                  autor['firstName'] == inscripto['firstName']):
                # Medium confidence - keep looking for better
                if best_match is None or best_match[0] < 2:
                    best_match = (2, "Media (apellido, nombre)", autor_name)

            else:
                # Low confidence - only if we haven't found better
                if best_match is None:
                    best_match = (1, "Baja (solo apellido)", autor_name)

    if best_match:
        return True, best_match[1], best_match[2]

    return False, "Sin coincidencia", None


# Define explicit column name patterns (order matters - first match wins)
LASTNAME_PATTERNS = ['apellido', 'apellidos', 'lastname', 'last_name', 'last name']
FIRSTNAME_PATTERNS = ['nombre', 'nombres', 'firstname', 'first_name', 'first name', 'primer nombre']
EMAIL_PATTERNS = ['email', 'correo', 'e-mail', 'mail', 'correo electronico']


def find_column(columns: List[str], patterns: List[str]) -> Optional[str]:
    """Find the first column that matches any of the patterns."""
    columns_lower = {col: str(col).lower() for col in columns}
    for pattern in patterns:
        for col, col_lower in columns_lower.items():
            if pattern == col_lower or pattern in col_lower:
                return col
    return None


def find_email_column(columns: List[str], author_num: int) -> Optional[str]:
    """Find the email column for a given author number."""
    # Try different email column naming patterns
    patterns = [
        f'Email.{author_num}',
        f'Email {author_num}',
        f'Email Autor {author_num}',
    ]
    # For first author, also try just 'Email'
    if author_num == 1:
        patterns = ['Email'] + patterns

    columns_lower = {str(col).lower(): col for col in columns}
    for pattern in patterns:
        pattern_lower = pattern.lower()
        if pattern_lower in columns_lower:
            return columns_lower[pattern_lower]
    for pattern in patterns:
        pattern_lower = pattern.lower()
        for col_lower, original_col in columns_lower.items():
            if pattern_lower == col_lower or pattern_lower in col_lower:
                return original_col
    return None


def extract_authors_from_row(row, df_columns) -> List[Dict[str, str]]:
    """Extract all authors from the individual author columns in a row"""
    authors = []

    # Check for up to 8 authors (based on the columns we saw)
    for i in range(1, 9):
        apellido_col = f'Apellido Autor {i}'
        nombre_col = f'Nombre Autor {i}'
        email_col = find_email_column(df_columns, i)

        # Check if these columns exist
        if apellido_col in df_columns:
            apellido = normalize_text(row[apellido_col])
            nombre = normalize_text(row[nombre_col]) if nombre_col in df_columns else ""
            email = normalize_text(row[email_col]) if email_col else ""

            # Only add if there's at least a last name
            if apellido:
                authors.append({
                    'lastName': apellido,
                    'firstName': nombre,
                    'email': email
                })

    return authors


# Streamlit UI
st.title("Chequeo de Autores - RADLA 2026")
st.write("Sube los archivos Excel para verificar si los autores de los trabajos estan inscriptos.")

trabajos_file = st.file_uploader("Archivo de Trabajos Finalizados", type=['xlsx'])
inscriptos_file = st.file_uploader("Archivo de Inscriptos", type=['xlsx'])

if trabajos_file is not None and inscriptos_file is not None:
    # Load the Excel files
    with st.spinner("Cargando archivos Excel..."):
        try:
            df_trabajos = pd.read_excel(trabajos_file)
            df_inscriptos = pd.read_excel(inscriptos_file)
        except Exception as exc:
            st.error("No se pudieron leer los archivos Excel. Verifica que sean .xlsx validos.")
            st.exception(exc)
            st.stop()

    with st.expander("Ver informacion de los archivos"):
        st.write(f"**Trabajos Finalizados:** {df_trabajos.shape[0]} filas, {df_trabajos.shape[1]} columnas")
        st.write(f"Columnas: {list(df_trabajos.columns)}")
        st.write(f"**Inscriptos:** {df_inscriptos.shape[0]} filas, {df_inscriptos.shape[1]} columnas")
        st.write(f"Columnas: {list(df_inscriptos.columns)}")

    # Detect columns for inscriptos
    lastname_col = find_column(df_inscriptos.columns, LASTNAME_PATTERNS)
    firstname_col = find_column(df_inscriptos.columns, FIRSTNAME_PATTERNS)
    email_col = find_column(df_inscriptos.columns, EMAIL_PATTERNS)

    with st.expander("Columnas detectadas en Inscriptos"):
        st.write(f"- Apellido: `{lastname_col}`")
        st.write(f"- Nombre: `{firstname_col}`")
        st.write(f"- Email: `{email_col}`")

    if not lastname_col:
        st.error(f"No se pudo detectar la columna de apellido en el archivo de Inscriptos. Columnas disponibles: {df_inscriptos.columns.tolist()}")
    else:
        # Parse inscriptos data
        inscriptos_parsed = []
        for idx, row in df_inscriptos.iterrows():
            person = {
                'lastName': normalize_text(row[lastname_col]) if lastname_col else "",
                'firstName': normalize_text(row[firstname_col]) if firstname_col else "",
                'email': normalize_text(row[email_col]) if email_col else ""
            }
            inscriptos_parsed.append(person)

        st.info(f"Se procesaron {len(inscriptos_parsed)} inscriptos")

        # Process each row in trabajos
        with st.spinner("Procesando trabajos..."):
            try:
                matches = []
                confidence_levels = []
                matched_authors = []

                for idx, row in df_trabajos.iterrows():
                    autores_list = extract_authors_from_row(row, df_trabajos.columns)
                    matched, confidence, author_name = check_match(autores_list, inscriptos_parsed)
                    matches.append("Si" if matched else "No")
                    confidence_levels.append(confidence)
                    matched_authors.append(author_name if author_name else "")

                # Add new columns
                df_trabajos['Autor_Encontrado_En_Inscriptos'] = matches
                df_trabajos['Nivel_Confianza'] = confidence_levels
                df_trabajos['Autor_Coincidente'] = matched_authors
            except Exception as exc:
                st.error("Ocurrio un error procesando los trabajos. Revisa las columnas del archivo.")
                st.exception(exc)
                st.stop()

        # Display results
        st.subheader("Resultados")

        total_trabajos = len(df_trabajos)
        total_matches = sum(1 for m in matches if m == "Si")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Trabajos", total_trabajos)
        with col2:
            st.metric("Con autor inscripto", total_matches)
        with col3:
            st.metric("Sin autor inscripto", total_trabajos - total_matches)

        st.write("**Distribucion por nivel de confianza:**")
        confidence_counts = (
            pd.Series(confidence_levels)
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Nivel de Confianza", 0: "Cantidad"})
        )
        st.dataframe(confidence_counts)

        with st.expander("Ver tabla completa de resultados"):
            df_trabajos_display = df_trabajos.copy()
            df_trabajos_display = (
                df_trabajos_display
                .where(df_trabajos_display.notna(), "")
                .astype(str)
            )
            st.dataframe(df_trabajos_display)

        # Download button
        output = BytesIO()
        df_trabajos.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        st.download_button(
            label="Descargar archivo actualizado",
            data=output,
            file_name="TrabajosFinalizados_Actualizado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Proceso completado!")
else:
    st.info("Por favor, sube ambos archivos Excel para comenzar el analisis.")
