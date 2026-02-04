import pandas as pd
import unicodedata
from typing import List, Tuple, Dict, Optional

# Load the Excel files
trabajos_file = r"C:\Users\herna\ChequearAutores\RADLA 2025 TrabajosFinalizados.xlsx"
inscriptos_file = r"C:\Users\herna\ChequearAutores\RADLA 2025  Inscriptos.xlsx"

print("Loading Excel files...")
df_trabajos = pd.read_excel(trabajos_file)
df_inscriptos = pd.read_excel(inscriptos_file)

print(f"\nTrabajos Finalizados shape: {df_trabajos.shape}")
print(f"Columns: {df_trabajos.columns.tolist()}")
print(f"\nInscriptos shape: {df_inscriptos.shape}")
print(f"Columns: {df_inscriptos.columns.tolist()}")

# Display first few rows to understand the structure
print("\n=== First rows of Trabajos Finalizados ===")
print(df_trabajos.head())
print("\n=== First rows of Inscriptos ===")
print(df_inscriptos.head())


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
    - "High (lastName, firstName, email)" - all three match
    - "Medium (lastName, firstName)" - lastName and firstName match
    - "Low (lastName only)" - only lastName matches
    - "No match" - no match found
    """
    if not autores_list:
        return False, "No match", None

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
                return True, "High (lastName, firstName, email)", autor_name

            elif (autor['firstName'] and
                  autor['firstName'] == inscripto['firstName']):
                # Medium confidence - keep looking for better
                if best_match is None or best_match[0] < 2:
                    best_match = (2, "Medium (lastName, firstName)", autor_name)

            else:
                # Low confidence - only if we haven't found better
                if best_match is None:
                    best_match = (1, "Low (lastName only)", autor_name)

    if best_match:
        return True, best_match[1], best_match[2]

    return False, "No match", None


# Parse inscriptos data - we need to identify which columns contain the relevant info
print("\n=== Parsing Inscriptos data ===")

# Define explicit column name patterns (order matters - first match wins)
LASTNAME_PATTERNS = ['apellido', 'apellidos', 'lastname', 'last_name', 'last name']
FIRSTNAME_PATTERNS = ['nombre', 'nombres', 'firstname', 'first_name', 'first name', 'primer nombre']
EMAIL_PATTERNS = ['email', 'correo', 'e-mail', 'mail', 'correo electronico']


def find_column(columns: List[str], patterns: List[str]) -> Optional[str]:
    """Find the first column that matches any of the patterns."""
    columns_lower = {col: col.lower() for col in columns}
    for pattern in patterns:
        for col, col_lower in columns_lower.items():
            if pattern == col_lower or pattern in col_lower:
                return col
    return None


# Detect columns once
lastname_col = find_column(df_inscriptos.columns, LASTNAME_PATTERNS)
firstname_col = find_column(df_inscriptos.columns, FIRSTNAME_PATTERNS)
email_col = find_column(df_inscriptos.columns, EMAIL_PATTERNS)

print(f"Detected columns - lastName: '{lastname_col}', firstName: '{firstname_col}', email: '{email_col}'")

if not lastname_col:
    print("WARNING: Could not detect lastName column in Inscriptos file!")
    print(f"Available columns: {df_inscriptos.columns.tolist()}")

inscriptos_parsed = []
for idx, row in df_inscriptos.iterrows():
    person = {
        'lastName': normalize_text(row[lastname_col]) if lastname_col else "",
        'firstName': normalize_text(row[firstname_col]) if firstname_col else "",
        'email': normalize_text(row[email_col]) if email_col else ""
    }
    inscriptos_parsed.append(person)

print(f"Parsed {len(inscriptos_parsed)} inscriptos")
print(f"Sample inscripto: {inscriptos_parsed[0] if inscriptos_parsed else 'None'}")

# Process each row in trabajos
print("\n=== Processing Trabajos Finalizados ===")

# Extract authors from individual columns (Apellido Autor 1-8, Nombre Autor 1-8, Email.1-8)
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

    for pattern in patterns:
        if pattern in columns:
            return pattern
    return None


def extract_authors_from_row(row) -> List[Dict[str, str]]:
    """Extract all authors from the individual author columns in a row"""
    authors = []

    # Check for up to 8 authors (based on the columns we saw)
    for i in range(1, 9):
        apellido_col = f'Apellido Autor {i}'
        nombre_col = f'Nombre Autor {i}'
        email_col = find_email_column(df_trabajos.columns, i)

        # Check if these columns exist
        if apellido_col in df_trabajos.columns:
            apellido = normalize_text(row[apellido_col])
            nombre = normalize_text(row[nombre_col]) if nombre_col in df_trabajos.columns else ""
            email = normalize_text(row[email_col]) if email_col else ""

            # Only add if there's at least a last name
            if apellido:
                authors.append({
                    'lastName': apellido,
                    'firstName': nombre,
                    'email': email
                })

    return authors

matches = []
confidence_levels = []
matched_authors = []

for idx, row in df_trabajos.iterrows():
    autores_list = extract_authors_from_row(row)

    matched, confidence, author_name = check_match(autores_list, inscriptos_parsed)
    matches.append("Yes" if matched else "No")
    confidence_levels.append(confidence)
    matched_authors.append(author_name if author_name else "")

# Add new columns
df_trabajos['Author_Found_In_Inscriptos'] = matches
df_trabajos['Match_Confidence'] = confidence_levels
df_trabajos['Matched_Author'] = matched_authors

# Save the updated file
output_file = r"C:\Users\herna\ChequearAutores\RADLA 2025 TrabajosFinalizados_Updated.xlsx"
df_trabajos.to_excel(output_file, index=False)

print(f"\n=== Results ===")
print(f"Total trabajos: {len(df_trabajos)}")
print(f"Matches found: {sum(1 for m in matches if m == 'Yes')}")
print(f"\nConfidence level distribution:")
print(pd.Series(confidence_levels).value_counts())
print(f"\nUpdated file saved to: {output_file}")
