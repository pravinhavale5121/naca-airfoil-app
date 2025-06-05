import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="NACA Airfoil Generator", layout="centered")

st.title("NACA 4-Digit Airfoil Generator")

# Step 1: User Inputs
naca_digits = st.text_input("Enter NACA 4-digit number (e.g., 2412)", max_chars=4)
chord_length = st.number_input("Enter Chord Length (in meters)", min_value=0.01, max_value=100.0, value=1.0)

# Step 2: Coordinate Generation Function
def generate_naca4_coordinates(naca, chord=1.0, num_points=100):
    m = int(naca[0]) / 100
    p = int(naca[1]) / 10
    t = int(naca[2:]) / 100

    x = np.linspace(0, 1, num_points)
    yt = 5 * t * (0.2969 * np.sqrt(x) -
                  0.1260 * x -
                  0.3516 * x**2 +
                  0.2843 * x**3 -
                  0.1015 * x**4)

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i in range(len(x)):
        if x[i] < p and p != 0:
            yc[i] = m / (p**2) * (2 * p * x[i] - x[i]**2)
            dyc_dx[i] = 2 * m / (p**2) * (p - x[i])
        elif p != 0:
            yc[i] = m / ((1 - p)**2) * ((1 - 2 * p) + 2 * p * x[i] - x[i]**2)
            dyc_dx[i] = 2 * m / ((1 - p)**2) * (p - x[i])

    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    x_coords = np.concatenate([xu[::-1], xl[1:]]) * chord
    y_coords = np.concatenate([yu[::-1], yl[1:]]) * chord

    return x_coords, y_coords

# Step 3: On Generate
if st.button("Generate Airfoil") and len(naca_digits) == 4 and naca_digits.isdigit():
    x_vals, y_vals = generate_naca4_coordinates(naca_digits, chord=chord_length)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, label=f"NACA {naca_digits}")
    ax.axis("equal")
    ax.grid(True)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"NACA {naca_digits} Airfoil (Chord = {chord_length} unit)")
    st.pyplot(fig)

    # Save to Excel
    df = pd.DataFrame({'x (m)': x_vals, 'y (m)': y_vals})
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Airfoil_Coords')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Click here to download airfoil coordinates (Excel)",
        data=excel_data,
        file_name=f"NACA_{naca_digits}_chord_{chord_length}m.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
elif len(naca_digits) == 4 and not naca_digits.isdigit():
    st.error("Please enter digits only (e.g., 2412)")
