import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
st.set_page_config(page_title="efts-group/CheckoutNet", layout="wide")




# Función principal
def main():
    mostrar_contenido()


def mostrar_contenido():
    # Crear columnas
    col1, col2 = st.columns([1, 2])  # Ajusta el tamaño de las columnas según sea necesario
    app_title = 'Welcome to CheckoutNet!'
    # Agregar el logo en la primera columna
    with col1:
        st.image("./img/efts_logo.png", width=150)  # Change the width as needed

    # Agregar el título en la segunda columna
    with col2:
        st.markdown(f"<h1 style='text-align: left;'>{app_title}</h1>", unsafe_allow_html=True)

    # Breve introducción
        # Centered title and introduction
    st.markdown("""
        <h2 style="text-align: center;">Understanding LTE Data Utilization in Mexico City 🚀</h2>
        <p style="text-align: center;">
            This application developed by EFTS Group, provides insights into LTE data usage patterns in Mexico City (CDMX) 📊 . 
            Explore average download speeds, upload speeds, and latency across various boroughs, 
            and gain valuable insights into how data is being utilized in this vibrant urban area. 
            Our app contains a 3-month forecast for each metric, allowing you to understand 
            future trends in data usage 📶.
        </p>
    """, unsafe_allow_html=True)


    # Cargar el archivo CSV con los datos de las series de tiempo
    @st.cache_data
    def load_data():
        df = pd.read_csv('./mnt/data_forecast_mvp.csv')
        df['ds'] = pd.to_datetime(df['ds'])  # Asegúrate de que la columna 'ds' esté en formato de fecha
        return df

    df = load_data()

    print(df.shape)

    # Cargar el archivo GeoJSON con los polígonos de los municipios
    geojson_file_path = './mnt/h3_cdmx.geojson'
    with open(geojson_file_path, 'r') as f:
        geojson_data = json.load(f)

    ### read median data 
    # Cargar el DataFrame con los promedios por H3
    @st.cache_data
    def load_h3_data():
        h3_df = pd.read_csv('./mnt/h3_median_data_cdmx.csv')  # Reemplaza con la ruta correcta de tu archivo
        return h3_df

    h3_df = load_h3_data()


    # Crear un contenedor para opciones de visualización que ocupa toda la anchura
    st.markdown('<h2 style="text-align: center;">Viz Options</h2>', unsafe_allow_html=True)

    options_container = st.container()

    with options_container:
        col1, col2, col3 = st.columns([1, 1, 1])  # Ajusta el ancho de las columnas según sea necesario

        with col1:
            municipio = st.selectbox("Select Municipality", df["municipio"].unique())

        with col2:
            operador = st.selectbox("Select Network Operator", df["operator"].unique())

        with col3:
            variable = st.selectbox("Select Variable", df["variable"].unique())


    # Filtrar los datos por municipio y operador
    filtered_df = df[(df['municipio'] == municipio) & (df['operator'] == operador) & (df['variable'] == variable)]
    #st.write("Contenido del DataFrame filtrado:", filtered_df)
    # Filtrar h3 

    filtered_h3 = h3_df[(h3_df['municipio'] == municipio) & (h3_df['operator'] == operador) & (h3_df['variable'] == variable)]

    if variable =='m_download_mbps':
        variable = 'download mbps'
    elif variable == 'm_upload_mbps':
        variable ='upload mbps'
    else:
        variable ='latency'
    # Crear el mapa con polígonos de los municipios
    st.markdown(f'<h2 style="text-align: center;">🛑 H3 Map average {variable} for {operador} in {municipio} </h2>', unsafe_allow_html=True)

    fig = px.choropleth_mapbox(
        filtered_h3,
        geojson=geojson_data,
        locations="h3_08", 
        featureidkey="properties.h3_08",  # Asegúrate de que el nombre de la propiedad en el geojson sea correcto
        color="median",  # Variable que se va a mostrar en el mapa
        mapbox_style="open-street-map",
        zoom=9, center={"lat": 19.4326, "lon": -99.1332},
        opacity=0.5,
    )

    fig.update_layout(height=600)
    st.plotly_chart(fig)

    # Mostrar la gráfica de la serie de tiempo
    # Crear la figura de la serie de tiempo
    fig = go.Figure()
    st.markdown(f'<h2 style="text-align: center;">📈 Time Series - {variable} Daily average for {operador} in {municipio}</h2>', unsafe_allow_html=True)

    # Agregar la serie de tiempo histórica
    historical_data = filtered_df[filtered_df['type'] == 'historical']
    fig.add_trace(go.Scatter(x=historical_data['ds'], y=historical_data['y'], mode='lines', name='Historic', line=dict(color='lightblue')))

    # Agregar el pronóstico (yhat) y sus límites
    forecast_data = filtered_df[filtered_df['type'] == 'forecast']

    # Agregar el pronóstico (yhat)
    fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['y'], mode='lines', name='Forecast', line=dict(color='orange')))

    # Agregar límites inferiores y superiores del pronóstico
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'],
        y=forecast_data['yhat_upper'],
        mode='lines',
        name='y_hat upper',
        line=dict(color='lightgreen'),
        fill='tonexty',  # Rellena hacia abajo
        fillcolor='rgba(144, 238, 144, 0.2)'  # Color de relleno
    ))

    fig.add_trace(go.Scatter(
        x=forecast_data['ds'],
        y=forecast_data['yhat_lower'],
        mode='lines',
        name='y_hat lower',
        line=dict(color='lightcoral'),
        fill='tonexty',  # Rellena hacia arriba
        fillcolor='rgba(255, 182, 193, 0.2)'  # Color de relleno
    ))

    # Actualizar el layout de la gráfica
    fig.update_layout(title=f"{variable} through time",
                    xaxis_title='Date',
                    yaxis_title=variable.capitalize(),
                    legend=dict(x=0, y=1))

    st.plotly_chart(fig)
    # Add the rights reserved image at the end

    # Agrega el aviso de derechos reservados
    st.markdown('<p style="text-align: center;width:10;">© 2024 Ookla® Data - All Rights Reserved.</p>', unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()
