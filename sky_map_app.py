import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import griddata
import io

st.set_page_config(page_title="Mapa de Brillo del Cielo", layout="centered")

st.title("Generador de Mapa de Brillo del Cielo en Proyección Polar")

# === FORMULARIO DEL USUARIO ===
st.sidebar.header("Datos del usuario")
nombre = st.sidebar.text_input("Nombre")
apellidos = st.sidebar.text_input("Apellidos")
institucion = st.sidebar.text_input("Institución")
archivo = st.sidebar.file_uploader("Sube tu archivo .ecsv", type=["ecsv", "csv"])

if archivo:
    # === LEER EL ARCHIVO ===
    try:
        df = pd.read_csv(archivo, comment='#')
        st.success("Archivo cargado correctamente.")

        # === PROCESAMIENTO DE DATOS ===
        r_points = 90 - df['Alt']
        theta_points = np.deg2rad(df['Azi'])
        mag_points = df['Mag']

        r_lin = np.linspace(0, 90, 500)
        theta_lin = np.linspace(0, 2 * np.pi, 500)
        theta_grid, r_grid = np.meshgrid(theta_lin, r_lin)

        interp_cubic = griddata((theta_points, r_points), mag_points, (theta_grid, r_grid), method='cubic')
        interp_nearest = griddata((theta_points, r_points), mag_points, (theta_grid, r_grid), method='nearest')
        brightness = np.where(np.isnan(interp_cubic), interp_nearest, interp_cubic)

        # === GRAFICAR ===
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
        ax.set_theta_zero_location('E')
        ax.set_theta_direction(-1)

        cmap = plt.get_cmap('viridis_r')
        norm = mcolors.Normalize(vmin=17, vmax=22.2)
        contourf = ax.contourf(theta_grid, r_grid, brightness, 100, cmap=cmap, norm=norm)
        contour_lines = ax.contour(theta_grid, r_grid, brightness,
                                   levels=np.arange(17.0, 22.2, 0.2), colors='white', linewidths=0.4)
        ax.clabel(contour_lines, fmt='%.1f', fontsize=7)

        ax.scatter(theta_points, r_points, c='red', s=4)
        ax.set_rlim(0, 90)
        ax.set_rticks(np.arange(10, 91, 10))
        ax.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
        ax.set_xticklabels(['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'])

        ax.set_title("Mapa de brillo del cielo", fontsize=14, pad=20)
        cbar_ax = fig.add_axes([0.2, 0.03, 0.6, 0.025])
        cbar = plt.colorbar(contourf, cax=cbar_ax, orientation='horizontal', ticks=np.arange(17, 22.5, 0.5))
        cbar.set_label('Sky Brightness [mag/arcsec²]', fontsize=10)

        st.pyplot(fig)

        # Mostrar datos del usuario
        st.markdown("---")
        st.subheader("Datos del usuario")
        st.markdown(f"**Nombre:** {nombre} {apellidos}")
        st.markdown(f"**Institución:** {institucion}")

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")

