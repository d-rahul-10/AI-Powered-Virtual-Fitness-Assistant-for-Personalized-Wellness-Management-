import streamlit as st

def calculate_bmi(weight, height):
    """Calculates BMI given weight in kg and height in cm."""
    if height <= 0:
        return None, "Height must be greater than 0."
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    return round(bmi, 2), None # Round BMI to 2 decimal places

def get_bmi_category(bmi):
    """Categorizes BMI based on standard ranges."""
    if bmi < 18.5:
        return "Underweight", "#1E90FF" # DodgerBlue
    elif 18.5 <= bmi < 25:
        return "Normal weight", "#32CD32" # LimeGreen
    elif 25 <= bmi < 30:
        return "Overweight", "#FFA500" # Orange
    else: # bmi >= 30
        return "Obese", "#FF6347" # Tomato

def show_bmi(user_data):
    """Displays the BMI calculation interface and results."""
    st.subheader("📏 Body Mass Index (BMI)")

    # Get initial values from user profile if available, otherwise use defaults
    initial_height = user_data.get('height', 170.0) # Default to 170 cm if not found
    initial_weight = user_data.get('weight', 70.0) # Default to 70 kg if not found

    # Input fields for height and weight
    height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=initial_height, step=0.1)
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=initial_weight, step=0.1)

    if st.button("Calculate BMI"):
        bmi, error = calculate_bmi(weight, height)
        if error:
            st.error(error)
        else:
            category, color = get_bmi_category(bmi)
            
            # Display BMI result with larger font and color coding
            st.markdown(f"### Your BMI: <span style='color:{color}; font-size: 24px;'>{bmi}</span>", unsafe_allow_html=True)
            st.markdown(f"**Category:** <span style='color:{color};'>{category}</span>", unsafe_allow_html=True)
            
            # Provide a brief explanation of BMI categories
            st.info(
                """
                **BMI Categories:**
                - **Underweight:** BMI less than 18.5
                - **Normal weight:** BMI 18.5 - 24.9
                - **Overweight:** BMI 25 - 29.9
                - **Obese:** BMI 30 or greater

                *Note: BMI is a screening tool and does not directly measure body fat. Consult a healthcare provider for a comprehensive health assessment.*
                """
            )