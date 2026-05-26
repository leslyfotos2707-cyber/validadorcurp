import streamlit as st
import pandas as pd
import re

def validar_curp(curp):

    curp = curp.strip().upper()

    patron = r'^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]$'

    if re.match(patron, curp):
        return "VÁLIDA"
    else:
        return "INCORRECTA"

st.title("Validador de CURP")

texto = st.text_area(
    "Pega las CURPs",
    height=250
)

if st.button("VALIDAR"):

    lista = texto.splitlines()

    resultados = []

    for curp in lista:

        curp = curp.strip()

        if curp:

            estado = validar_curp(curp)

            resultados.append({
                "CURP": curp,
                "ESTATUS": estado
            })

    df = pd.DataFrame(resultados)

    st.dataframe(df)
