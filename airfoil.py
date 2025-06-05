import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import comb
from io import BytesIO

def naca4(m, p, t, chord, num_points=100):
    x = np.linspace(0, 1, num_points)
    yt = 5 * t * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )

    yc = np.where(
        x < p,
        m / (p ** 2) * (2 * p * x - x ** 2),
        m / ((1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x - x ** 2)
    )

    dyc_dx = np.where(
        x < p,
        2 * m / p ** 2 * (p - x),
        2 * m / (1 - p) ** 2 * (p - x)
    )

    theta = np.arctan(dyc_dx)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    x_coords = np.concatenate([xu[::-1], xl[1:]]) * chord
    y_coords = np.concatenate([yu[::-1], yl[1:]]) * chord

    return x_coords, y_coords

# Placeholder for 5-digit and 6-digit — use proper generation later
def naca_placeholder(series, chord, num_points=100):
    x = np.linspace(0, 1, num_points)
    y = 0.1 * np.sin(2 * np.pi * x)
    return x * chord, y * chord

# Streamlit UI
st.title("✈️ NACA Airfoil Generator")
series = st.selectbox("Select NACA Series", ["4-digit", "5-digit", "6-digit"])

digits = st.text_input("Enter NACA Digits (e.g., 2412 for 4-digit):")
chord = st.number_input("Chord Length (in meters)", min_value=0.01, value=1.0)

if st.button("Generate Airfoil"):
    if series == "4-digit" and len(digits) == 4 and digits.isdigit():
        m = int(digits[0]) / 100
        p = int(digits[1]) / 10
        t = int(digits[2:]) / 100
        x, y = naca4(m, p, t, chord)
    elif series in ["5-digit", "6-digit"] and digits.isdigit():
        x, y = naca_placeholder(series, chord)
    else:
        st.error("Invalid input. Please check your digits.")
        st.stop()

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_aspect("equal")
    ax.set_title(f"NACA {digits} Airfoil")
    st.pyplot(fig)

    # Download as Excel
    df = pd.DataFrame({"X": x, "Y": y})
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    st.download_button("📥 Download Coordinates (Excel)", excel_file.getvalue(), file_name=f"NACA_{digits}_coords.xlsx")

