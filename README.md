# Chequeo de Autores - RADLA 2026

Aplicacion web para verificar si los autores de trabajos finalizados estan inscriptos en el congreso, y para procesar archivos de becados.

## Acceso a la Aplicacion

La aplicacion esta disponible en: **https://chequeoautores.streamlit.app/**

---

## IMPORTANTE: Formato de Archivos

> **Los archivos DEBEN estar en formato Excel (.xlsx)**
>
> **Los nombres de las columnas DEBEN coincidir con los esperados**
>
> El sistema normaliza automaticamente mayusculas/minusculas y acentos, pero la estructura basica debe ser correcta.

---

## Archivos Requeridos

### 1. Archivo de Trabajos Finalizados (obligatorio)

Este archivo contiene la informacion de los trabajos presentados.

**Columnas requeridas:**
| Columna | Descripcion |
|---------|-------------|
| `Trabajo` | ID numerico del trabajo |
| `Titulo` | Titulo del trabajo |
| `Autores` | Lista de autores separados por coma |
| `Apellido Autor 1` | Apellido del primer autor |
| `Nombre Autor 1` | Nombre del primer autor |
| `Email` o `Email.1` | Email del primer autor |
| `Apellido Autor 2`, `Nombre Autor 2`, etc. | Datos de autores adicionales (hasta 8) |

**Archivo de ejemplo:** [RADLA 2025 TrabajosFinalizados.xlsx](samples/RADLA%202025%20TrabajosFinalizados.xlsx)

---

### 2. Archivo de Inscriptos (obligatorio)

Este archivo contiene la lista de personas inscriptas al congreso.

**Columnas requeridas:**
| Columna | Descripcion |
|---------|-------------|
| `Id Inscripto` | ID unico del inscripto |
| `Apellido` | Apellido de la persona |
| `Nombre` | Nombre de la persona |
| `E-Mail` | Correo electronico |

**Archivo de ejemplo:** [RADLA 2025 Inscriptos.xlsx](samples/RADLA%202025%20%20Inscriptos.xlsx)

---

### 3. Archivo de Becados (opcional)

Este archivo contiene la lista de becados que se desea verificar.

**Columnas requeridas:**
| Columna | Descripcion |
|---------|-------------|
| `Pais` | Pais del becado |
| `Nombre` | Nombre del becado |
| `Apellido` | Apellido del becado |
| `e-mail` | Correo electronico |
| `Titulo del Trabajo` | Titulo del trabajo presentado |

**Archivo de ejemplo:** [2026 01 30 Becados Todos (1).xlsx](samples/2026%2001%2030%20Becados%20Todos%20(1).xlsx)

---

## Instrucciones de Uso Paso a Paso

### Paso 1: Subir los Archivos

1. **Archivo de Trabajos Finalizados** (obligatorio)
   - Haga clic en "Browse files" debajo de "Archivo de Trabajos Finalizados"
   - Seleccione su archivo .xlsx con los trabajos

2. **Archivo de Inscriptos** (obligatorio)
   - Haga clic en "Browse files" debajo de "Archivo de Inscriptos"
   - Seleccione su archivo .xlsx con los inscriptos

3. **Archivo de Becados** (opcional)
   - Si desea procesar becados, suba el archivo usando el tercer boton

### Paso 2: Verificar los Archivos Cargados

Una vez subidos los archivos, la aplicacion mostrara un resumen:
- Cantidad de filas en cada archivo
- Puede expandir "Ver informacion de los archivos" para ver las columnas detectadas

> **IMPORTANTE:** Verifique que las columnas detectadas sean correctas antes de continuar.

### Paso 3: Hacer Clic en "Procesar"

Una vez que haya subido todos los archivos necesarios:
1. Haga clic en el boton **"Procesar"**
2. Espere a que la aplicacion procese los datos

### Paso 4: Ver los Resultados

Despues de procesar, la aplicacion mostrara:

**Para Trabajos:**
- **Total Trabajos**: Cantidad de trabajos procesados
- **Con autor inscripto**: Trabajos donde al menos un autor esta inscripto
- **Sin autor inscripto**: Trabajos sin ningun autor inscripto
- **Nivel de confianza**: Indica que tan seguro es el match
  - *Alta*: Coincide apellido, nombre y email
  - *Media*: Coincide apellido y nombre
  - *Baja*: Solo coincide el apellido

**Para Becados (si se subio el archivo):**
- **Total Becados**: Cantidad de becados procesados
- **Con Id Inscripto**: Becados encontrados en la lista de inscriptos
- **Con Trabajo Id**: Becados cuyo trabajo fue encontrado

### Paso 5: Descargar Archivos Procesados

**Archivo de Trabajos Actualizado:**
Haga clic en "Descargar archivo actualizado" para obtener el archivo con las columnas adicionales:
- `Autor_Encontrado_En_Inscriptos`: Si/No
- `Nivel_Confianza`: Alta/Media/Baja/Sin coincidencia
- `Autor_Coincidente`: Nombre del autor que coincidio

**Archivo de Becados Actualizado (si aplica):**
Haga clic en "Descargar archivo de Becados actualizado" para obtener el archivo con:
- `Id Inscripto`: ID del inscripto si se encuentra por nombre y apellido
- `Trabajo Id`: ID del trabajo si el titulo coincide exactamente y el becado aparece como autor

---

## Notas Importantes

1. **Formato obligatorio**: Solo se aceptan archivos Excel con extension `.xlsx`

2. **Nombres de columnas**: Deben ser similares a los indicados. El sistema tolera variaciones menores como:
   - Mayusculas/minusculas (`APELLIDO` = `apellido` = `Apellido`)
   - Acentos (`Título` = `Titulo`)
   - Espacios extras

3. **Matching de titulos**: Para el archivo de Becados, el titulo debe coincidir **exactamente** (despues de normalizar) con el titulo en Trabajos Finalizados

4. **Verificacion de autores**: Ademas del titulo, se verifica que el nombre del becado aparezca en la lista de autores del trabajo

---

## Archivos de Ejemplo

Puede descargar archivos de ejemplo para entender el formato esperado:

- [Trabajos Finalizados](samples/RADLA%202025%20TrabajosFinalizados.xlsx)
- [Inscriptos](samples/RADLA%202025%20%20Inscriptos.xlsx)
- [Becados](samples/2026%2001%2030%20Becados%20Todos%20(1).xlsx)

---

## Soporte

Si tiene problemas con la aplicacion, verifique:
1. Que los archivos esten en formato .xlsx
2. Que las columnas tengan los nombres correctos
3. Que no haya filas vacias al inicio del archivo
