import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Validador CURP", layout="wide")

ENTIDADES = {
    "AS": "Aguascalientes", "BC": "Baja California", "BS": "Baja California Sur",
    "CC": "Campeche", "CL": "Coahuila", "CM": "Colima", "CS": "Chiapas",
    "CH": "Chihuahua", "DF": "Ciudad de México", "DG": "Durango",
    "GT": "Guanajuato", "GR": "Guerrero", "HG": "Hidalgo", "JC": "Jalisco",
    "MC": "Estado de México", "MN": "Michoacán", "MS": "Morelos",
    "NT": "Nayarit", "NL": "Nuevo León", "OC": "Oaxaca", "PL": "Puebla",
    "QT": "Querétaro", "QR": "Quintana Roo", "SP": "San Luis Potosí",
    "SL": "Sinaloa", "SR": "Sonora", "TC": "Tabasco", "TS": "Tamaulipas",
    "TL": "Tlaxcala", "VZ": "Veracruz", "YN": "Yucatán", "ZS": "Zacatecas",
    "NE": "Nacido en el extranjero"
}

def validar_curp(curp):
    curp = str(curp).strip().upper()
    patron = r'^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]$'
    return bool(re.match(patron, curp))

def obtener_genero(curp):
    curp = str(curp).strip().upper()
    if len(curp) >= 11:
        return "Femenino" if curp[10] == "M" else "Masculino" if curp[10] == "H" else ""
    return ""

def obtener_estado(curp):
    curp = str(curp).strip().upper()
    if len(curp) >= 13:
        clave = curp[11:13]
        return ENTIDADES.get(clave, "")
    return ""

def procesar_lista(df):
    resultados = []

    for _, fila in df.iterrows():
        curp = str(fila.get("CURP", "")).strip().upper()
        nombre = fila.get("Nombre Completo", "")
        localidad = fila.get("Municipio, Estado", "")

        if curp:
            resultados.append({
                "Nombre Completo": nombre,
                "CURP": curp,
                "Municipio, Estado": localidad if localidad else obtener_estado(curp),
                "Sexo": fila.get("Sexo", "") if fila.get("Sexo", "") else obtener_genero(curp),
                "Estatus CURP": "VÁLIDA" if validar_curp(curp) else "INCORRECTA"
            })

    return pd.DataFrame(resultados)

def convertir_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return output.getvalue()

st.title("Validador de CURP")
st.write("Carga un Excel o pega tus CURPs para validar la información.")

opcion = st.radio(
    "Selecciona una opción:",
    ["Pegar CURPs", "Subir Excel"]
)

if opcion == "Pegar CURPs":
    texto = st.text_area("Pega una CURP por línea", height=250)

    if st.button("Validar CURPs"):
        lista = texto.splitlines()

        df = pd.DataFrame({
            "Nombre Completo": ["" for _ in lista],
            "CURP": lista,
            "Municipio, Estado": ["" for _ in lista],
            "Sexo": ["" for _ in lista]
        })

        resultado = procesar_lista(df)

        st.dataframe(resultado, use_container_width=True)

        archivo_excel = convertir_excel(resultado)

        st.download_button(
            label="Descargar Excel",
            data=archivo_excel,
            file_name="resultado_curps.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if opcion == "Subir Excel":
    archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

    st.info("Tu Excel debe tener una columna llamada CURP. Opcionalmente puede tener: Nombre Completo, Municipio, Estado y Sexo.")

    if archivo:
        df = pd.read_excel(archivo)

        if "CURP" not in df.columns:
            st.error("El archivo debe tener una columna llamada CURP.")
        else:
            resultado = procesar_lista(df)

            st.dataframe(resultado, use_container_width=True)

            archivo_excel = convertir_excel(resultado)

            st.download_button(
                label="Descargar Excel",
                data=archivo_excel,
                file_name="resultado_curps.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
