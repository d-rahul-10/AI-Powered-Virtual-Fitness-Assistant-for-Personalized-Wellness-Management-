import streamlit as st
from db import query_db, execute_db


def manage_profile(user_id):
    """Displays the user profile and allows editing."""
    st.subheader("👤 Manage Profile")

    # Fetch current user data from the database
    user_data = query_db(
        "SELECT name, email, age, gender, height, weight FROM users WHERE id = ?",
        (user_id,),
        fetchone=True
    )

    if not user_data:
        st.error("User data could not be retrieved.")
        return

    age = int(user_data['age']) if user_data['age'] else 25
    gender = user_data['gender'] if user_data['gender'] else "Male"
    height = float(user_data['height']) if user_data['height'] else 170.0
    weight = float(user_data['weight']) if user_data['weight'] else 70.0

    # Show current BMI at the top as a quick summary
    if height > 0:
        bmi = weight / ((height / 100) ** 2)
        bmi_category = _get_bmi_category(bmi)
        cA, cB, cC = st.columns(3)
        cA.metric("Current Weight", f"{weight:.1f} kg")
        cB.metric("Height", f"{height:.0f} cm")
        cC.metric("BMI", f"{bmi:.1f}  ({bmi_category})")

    st.divider()

    # Editable form
    with st.form("profile_form"):
        new_name = st.text_input("Name", value=user_data['name'])
        new_age = st.number_input("Age", min_value=1, max_value=120, value=age)
        gender_options = ["Male", "Female", "Other"]
        new_gender = st.selectbox(
            "Gender",
            options=gender_options,
            index=gender_options.index(gender)
        )
        new_height = st.number_input(
            "Height (cm)", min_value=50.0, max_value=250.0, value=height, step=0.1
        )
        new_weight = st.number_input(
            "Weight (kg)", min_value=20.0, max_value=300.0, value=weight, step=0.1
        )
        submitted = st.form_submit_button("💾 Update Profile", type="primary", use_container_width=True)

    if submitted:
        if not new_name.strip():
            st.error("Name cannot be empty.")
        else:
            result = execute_db(
                "UPDATE users SET name = ?, age = ?, gender = ?, height = ?, weight = ? WHERE id = ?",
                (new_name.strip(), new_age, new_gender, new_height, new_weight, user_id)
            )
            if result != -1:
                st.success("✅ Profile updated successfully!")
                # Keep session state in sync so the sidebar name updates immediately
                if "user" in st.session_state:
                    st.session_state.user["name"] = new_name.strip()
                    st.session_state.user["age"] = new_age
                    st.session_state.user["gender"] = new_gender
                    st.session_state.user["height"] = new_height
                    st.session_state.user["weight"] = new_weight
                st.rerun()
            else:
                st.error("Failed to update profile. Please try again.")

    # Read-only info card
    with st.expander("📋 Current Profile Info"):
        st.markdown(f"- **Name:** {user_data['name']}")
        st.markdown(f"- **Email:** {user_data['email']}")
        st.markdown(f"- **Age:** {age}")
        st.markdown(f"- **Gender:** {gender}")
        st.markdown(f"- **Height:** {height} cm")
        st.markdown(f"- **Weight:** {weight} kg")


def _get_bmi_category(bmi: float) -> str:
    """Returns a short BMI category label."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    return "Obese"
