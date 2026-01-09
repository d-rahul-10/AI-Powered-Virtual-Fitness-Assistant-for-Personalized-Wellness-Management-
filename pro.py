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

    # Pre-populate the form with current data
    name = user_data['name']
    email = user_data['email'] # Note: Updating email might require additional checks for uniqueness
    age = int(user_data['age']) if user_data['age'] else 25 # Default if NULL
    gender = user_data['gender'] if user_data['gender'] else "Male"
    height = float(user_data['height']) if user_data['height'] else 170.0
    weight = float(user_data['weight']) if user_data['weight'] else 70.0

    # Create input fields for profile details
    new_name = st.text_input("Name", value=name)
    # new_email = st.text_input("Email", value=email) # Consider carefully if allowing email change
    new_age = st.number_input("Age", min_value=1, max_value=120, value=age)
    new_gender = st.selectbox("Gender", options=["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender))
    new_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=height, step=0.1)
    new_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=weight, step=0.1)

    if st.button("Update Profile"):
        # Update the user's profile in the database
        # If allowing email update, add email validation and uniqueness check here
        result = execute_db(
            "UPDATE users SET name = ?, age = ?, gender = ?, height = ?, weight = ? WHERE id = ?",
            (new_name, new_age, new_gender, new_height, new_weight, user_id)
        )
        if result != -1:
            st.success("Profile updated successfully!")
            # Optionally, update session state user data if needed elsewhere immediately
            # st.session_state.user.update({...}) # Update relevant fields
            st.rerun() # Refresh the view to show updated data
        else:
            st.error("Failed to update profile. Please try again.")

    # Display current profile information (after potential update)
    st.subheader("Your Current Information")
    st.write(f"**Name:** {name}")
    st.write(f"**Email:** {email}") # Display email even if not editable here
    st.write(f"**Age:** {age}")
    st.write(f"**Gender:** {gender}")
    st.write(f"**Height:** {height} cm")
    st.write(f"**Weight:** {weight} kg")

    # Optional: Add a BMI calculation display here based on current height/weight
    if height > 0 and weight > 0:
        bmi = weight / ((height / 100) ** 2)
        st.write(f"**Calculated BMI:** {bmi:.2f}")
