import streamlit as st
import plotly.graph_objects as go


def calculate_bmi(weight, height):
    """Calculates BMI given weight in kg and height in cm."""
    if height <= 0:
        return None, "Height must be greater than 0."
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2), None


def get_bmi_category(bmi):
    """Categorises BMI based on standard ranges. Returns (category, color)."""
    if bmi < 18.5:
        return "Underweight", "#1E90FF"
    elif bmi < 25:
        return "Normal weight", "#32CD32"
    elif bmi < 30:
        return "Overweight", "#FFA500"
    else:
        return "Obese", "#FF6347"


def _bmi_gauge(bmi: float, color: str) -> go.Figure:
    """Returns a Plotly gauge chart for the given BMI value."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmi,
        number={"suffix": "", "font": {"size": 28}},
        gauge={
            "axis": {"range": [10, 40], "tickwidth": 1, "tickcolor": "gray"},
            "bar": {"color": color, "thickness": 0.3},
            "steps": [
                {"range": [10, 18.5], "color": "#cce5ff"},    # Underweight – blue tint
                {"range": [18.5, 25], "color": "#d4edda"},    # Normal – green tint
                {"range": [25, 30],  "color": "#fff3cd"},    # Overweight – amber tint
                {"range": [30, 40],  "color": "#f8d7da"},    # Obese – red tint
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": bmi,
            },
        },
        title={"text": "BMI Gauge", "font": {"size": 16}},
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=20, l=30, r=30))
    return fig


def calculate_bmr(weight, height, age, gender):
    """Calculates Basal Metabolic Rate (BMR) from user metrics."""
    if height <= 0 or age <= 0 or weight <= 0:
        return None

    gender_tag = (gender or "").strip().lower()
    if gender_tag == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    elif gender_tag == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        # Use average of male and female formulas for non-binary/other
        bmr_male = 10 * weight + 6.25 * height - 5 * age + 5
        bmr_female = 10 * weight + 6.25 * height - 5 * age - 161
        bmr = (bmr_male + bmr_female) / 2

    return round(bmr, 2)


def calculate_tdee(bmr, activity_level):
    """Calculates Total Daily Energy Expenditure based on activity multiplier."""
    if bmr is None:
        return None

    factors = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (1-3 days/week)": 1.375,
        "Moderately active (3-5 days/week)": 1.55,
        "Very active (6-7 days/week)": 1.725,
        "Extra active (very hard exercise / physical job)": 1.9,
    }

    multiplier = factors.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)


def show_bmi(user_data):
    """Displays the BMI calculation interface and results."""
    st.subheader("📏 Body Mass Index (BMI)")

    initial_height = user_data.get('height', 170.0)
    initial_weight = user_data.get('weight', 70.0)
    initial_age = user_data.get('age', 25)
    initial_gender = user_data.get('gender', 'Male')

    col_l, col_r = st.columns(2)
    with col_l:
        height = st.number_input(
            "Height (cm)", min_value=50.0, max_value=250.0, value=float(initial_height), step=0.1
        )
        age = st.number_input(
            "Age", min_value=1, max_value=120, value=int(initial_age), step=1
        )
        activity_level = st.selectbox(
            "Activity Level",
            options=[
                "Sedentary (little or no exercise)",
                "Lightly active (1-3 days/week)",
                "Moderately active (3-5 days/week)",
                "Very active (6-7 days/week)",
                "Extra active (very hard exercise / physical job)",
            ],
            index=0,
        )

    with col_r:
        weight = st.number_input(
            "Weight (kg)", min_value=20.0, max_value=300.0, value=float(initial_weight), step=0.1
        )
        gender = st.selectbox(
            "Gender",
            options=["Male", "Female", "Other"],
            index=["Male", "Female", "Other"].index(str(initial_gender)) if str(initial_gender) in ["Male", "Female", "Other"] else 0
        )

    if st.button("Calculate BMI & Calories", type="primary", use_container_width=True):
        bmi, error = calculate_bmi(weight, height)
        if error:
            st.error(error)
            return

        category, color = get_bmi_category(bmi)

        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_level)
        lose_cal = round(max(tdee - 500, 1200), 2)
        gain_cal = round(tdee + 500, 2)

        # Gauge chart
        st.plotly_chart(_bmi_gauge(bmi, color), use_container_width=True)

        # Result text
        st.markdown(
            f"<h3 style='text-align:center;'>BMI: "
            f"<span style='color:{color};'>{bmi}</span> — "
            f"<span style='color:{color};'>{category}</span></h3>",
            unsafe_allow_html=True,
        )

        # Ideal weight range
        ideal_low = round(18.5 * ((height / 100) ** 2), 1)
        ideal_high = round(24.9 * ((height / 100) ** 2), 1)

        st.info(
            f"**Ideal weight range** for your height: **{ideal_low} kg – {ideal_high} kg**\n\n"
            "**BMI Reference:**\n"
            "- 🔵 Underweight: < 18.5\n"
            "- 🟢 Normal weight: 18.5 – 24.9\n"
            "- 🟠 Overweight: 25 – 29.9\n"
            "- 🔴 Obese: ≥ 30\n\n"
            "*BMI is a screening tool and does not directly measure body fat. "
            "Consult a healthcare provider for a comprehensive health assessment.*"
        )

        st.markdown("### 🔥 Calorie Estimates")
        st.markdown(f"- **BMR (Basal Metabolic Rate):** {bmr} kcal/day")
        st.markdown(f"- **TDEE (total daily energy expenditure)** [{activity_level}]: {tdee} kcal/day")
        st.markdown(f"- **Maintenance calories:** {tdee} kcal/day")
        st.markdown(f"- **Weight loss target (approx -500 kcal/day):** {lose_cal} kcal/day")
        st.markdown(f"- **Weight gain target (approx +500 kcal/day):** {gain_cal} kcal/day")

        st.success("✅ Calorie and BMI calculations completed successfully!")
