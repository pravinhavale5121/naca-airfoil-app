import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="NACA Airfoil Generator", layout="centered")

st.title("NACA Airfoil Generator (4-, 5-, and 6-digit Series)")

# --- Helper functions ---

def generate_naca4(naca, chord=1.0, num_points=100):
    m = int(naca[0]) / 100
    p = int(naca[1]) / 10
    t = int(naca[2:]) / 100

    x = np.linspace(0, 1, num_points)
    yt = 5 * t * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i in range(len(x)):
        if x[i] < p and p != 0:
            yc[i] = m / (p**2) * (2*p*x[i] - x[i]**2)
            dyc_dx[i] = 2*m / (p**2) * (p - x[i])
        elif p != 0:
            yc[i] = m / ((1-p)**2) * ((1 - 2*p) + 2*p*x[i] - x[i]**2)
            dyc_dx[i] = 2*m / ((1-p)**2) * (p - x[i])

    theta = np.arctan(dyc_dx)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    x_coords = np.concatenate([xu[::-1], xl[1:]]) * chord
    y_coords = np.concatenate([yu[::-1], yl[1:]]) * chord

    return x_coords, y_coords

def generate_naca5(naca, chord=1.0, num_points=100):
    # 5-digit NACA airfoils are more complex; this is a simplified camber line for reflexed or normal
    # We assume no reflex here (last digit = 0)
    # Format: [first digit]=design lift coefficient * 0.15; second and third = position of max camber; last two digits = thickness
    cld = int(naca[0]) * 0.15  # design lift coefficient
    p = int(naca[1:3]) / 20  # position of max camber
    t = int(naca[3:5]) / 100

    x = np.linspace(0,1,num_points)
    yt = 5 * t * (0.2969*np.sqrt(x) - 0.126*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i in range(len(x)):
        if x[i] < p and p != 0:
            yc[i] = (cld / 6) * (3*p**2 - 6*p*x[i] + 4*x[i]**2)
            dyc_dx[i] = (cld / 6) * (-6*p + 8*x[i])
        elif p != 0:
            yc[i] = (cld / 6) * (3*p**2 - 6*p*x[i] + 4*x[i]**2)
            dyc_dx[i] = (cld / 6) * (-6*p + 8*x[i])

    theta = np.arctan(dyc_dx)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    x_coords = np.concatenate([xu[::-1], xl[1:]]) * chord
    y_coords = np.concatenate([yu[::-1], yl[1:]]) * chord

    return x_coords, y_coords

def generate_naca6(naca, chord=1.0, num_points=100):
    # NACA 6-series airfoils are complex; simplified version generating symmetric shape
    # Format: NACA 63-xxx or similar; for demo, only thickness handled, camber = 0
    t = int(naca[-3:]) / 100

    x = np.linspace(0,1,num_points)
    yt = 5 * t * (0.2969*np.sqrt(x) - 0.126*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)

    # Symmetric airfoil (no camber)
    x_coords = np.concatenate([x[::-1], x[1:]]) * chord
    y_coords = np.concatenate([yt[::-1], -yt[1:]]) * chord

    return x_coords, y_coords

# --- UI ---

series = st.selectbox("Select NACA Series", options=["4-digit", "5-digit", "6-digit"])

if series == "4-digit":
    naca = st.text_input("Enter NACA 4-digit number (e.g., 2412)", max_chars=4)
elif series == "5-digit":
    naca = st.text_input("Enter NACA 5-digit number (e.g., 23012)", max_chars=5)
else:
    naca = st.text_input("Enter NACA 6-digit number (e.g., 63012)", max_chars=6)

chord_length = st.number_input("Enter chord length (meters)", min_value=0.01, max_value=100.0, value=1.0)

if st.button("Generate Airfoil"):
    if (series == "4-digit" and len(naca) == 4 and naca.isdigit()) or \
       (series == "5-digit" and len(naca) == 5 and naca.isdigit()) or \
       (series == "6-digit" and len(naca) == 6 and naca.isdigit()):
        
        if series == "4-digit":
            x_vals, y_vals = generate_naca4(naca, chord=chord_length)
        elif series == "5-digit":
            x_vals, y_vals = generate_naca5(naca, chord=chord_length)
        else:
            x_vals, y_vals = generate_naca6(naca, chord=chord_length)

        # Plot
        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals, label=f"NACA {naca}")
        ax.axis('equal')
        ax.grid(True)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_title(f"NACA {naca} Airfoil (Chord={chord_length} m)")
        st.pyplot(fig)

        # Save to Excel
        df = pd.DataFrame({'x (m)': x_vals, 'y (m)': y_vals})
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Airfoil_Coords')
        excel_data = output.getvalue()

        st.download_button(
            label="Download coordinates (Excel)",
            data=excel_data,
            file_name=f"NACA_{naca}_chord_{chord_length}m.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Please enter valid digits for the selected series.")
