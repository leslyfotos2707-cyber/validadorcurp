import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Validador de CURP", layout="wide")

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

def obtener_sexo(curp):
    curp = str(curp).strip().upper()
    if len(curp) >= 11:
        if curp[10] == "M":
            return "Femenino"
        elif curp[10] == "H":
            return "Masculino"
    return ""

def obtener_estado(curp):
    curp = str(curp).strip().upper()
    if len(curp) >= 13:
        return ENTIDADES.get(curp[11:13], "")
    return ""

def obtener_fecha(curp):
    curp = str(curp).strip().upper()
    if len(curp) >= 10:
        año = curp[4:6]
        mes = curp[6:8]
        dia = curp[8:10]

        año_completo = "19" + año if int(año) > 30 else "20" + año
        return f"{dia}/{mes}/{año_completo}"
    return ""

def convertir_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return output.getvalue()

st.title("Validador de CURP con Nombre y Localidad")

st.write("Sube un Excel con las columnas: Nombre Completo, CURP y Localidad.")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    columnas_requeridas = ["Nombre Completo", "CURP", "Localidad"]

    faltantes = [col for col in columnas_requeridas if col not in df.columns]

    if faltantes:
        st.error(f"Faltan estas columnas en tu Excel: {', '.join(faltantes)}")
    else:
        resultados = []

        for _, fila in df.iterrows():
            curp = str(fila["CURP"]).strip().upper()

            resultados.append({
                "Nombre Completo": fila["Nombre Completo"],
                "CURP": curp,
                "Localidad": fila["Localidad"],
                "Sexo": obtener_sexo(curp),
                "Fecha de Nacimiento": obtener_fecha(curp),
                "Estado de Nacimiento": obtener_estado(curp),
                "Estatus CURP": "VÁLIDA" if validar_curp(curp) else "INCORRECTA"
            })

        resultado = pd.DataFrame(resultados)

        st.subheader("Resultados")
        st.dataframe(resultado, use_container_width=True)

        validos = resultado[resultado["Estatus CURP"] == "VÁLIDA"]
        incorrectos = resultado[resultado["Estatus CURP"] == "INCORRECTA"]

        st.success(f"CURPs válidas: {len(validos)}")
        st.error(f"CURPs incorrectas: {len(incorrectos)}")

        archivo_excel = convertir_excel(resultado)

        st.download_button(
            label="Descargar resultados en Excel",
            data=archivo_excel,
            file_name="resultado_curps.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
