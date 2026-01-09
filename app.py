import streamlit as st
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

# Import all necessary modules
from auth import register, login
from bmi import show_bmi
from pro import manage_profile
from workouts import log_workout
from tips import show_tip
from dashboard import show_dashboard
from goals import set_goal, view_goals
from report_generator import generate_user_report
from chatbot import fitness_chatbot, show_chat_analytics
from nutrition_chat import nutrition_chat  # ✅ Nutrition assistant

# Set page configuration
st.set_page_config("Fitness Assistant", layout="wide")

def main():
    # Check if user is logged in (user_id in session state)
    if "user_id" not in st.session_state:
        # Show Login/Register options in sidebar
        page = st.sidebar.selectbox("Menu", ["Login", "Register"])
        if page == "Login":
            login()
        else:
            register()
    else:
        # User is logged in
        # Try to display logo, handle error if file not found
        try:
            st.sidebar.image("Logo.png", width=120)
        except FileNotFoundError:
            st.sidebar.warning("Logo.png not found. Using default header.")
            st.sidebar.markdown("**Fitness Assistant**")
        
        # Display welcome message with user's name
        st.sidebar.markdown(f"👋 Hello, **{st.session_state.user['name']}**")
        
        # Show a random tip
        show_tip(st.session_state.user_id)

        # Welcome banner
        st.markdown("""
        <div style='text-align:center; padding: 10px 0;'>
            <h2 style='color:#FF6B6B;'>🏋️ Welcome to <b>Fitness Assistant</b></h2>
            <p style='font-size:16px'>AI-powered fitness insights at your fingertips.</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation menu in sidebar
        choice = st.sidebar.radio(
            "📂 Navigation",
            ["Dashboard", "BMI", "Profile", "Workout", "Goals", "Chatbot", "Nutrition", "Report", "Logout"]
        )

        # Handle logout
        if choice == "Logout":
            st.session_state.clear()
            st.rerun() # Use st.rerun() instead of deprecated st.experimental_rerun()

        # Route to selected page based on choice
        elif choice == "Dashboard":
            show_dashboard(st.session_state.user_id)

        elif choice == "BMI":
            show_bmi(st.session_state.user) # Pass the entire user dict for BMI calculation

        elif choice == "Profile":
            manage_profile(st.session_state.user_id)

        elif choice == "Workout":
            log_workout(st.session_state.user_id)

        elif choice == "Goals":
            set_goal(st.session_state.user_id)
            view_goals(st.session_state.user_id)

        elif choice == "Chatbot":
            fitness_chatbot(st.session_state.user_id)
            with st.expander("📊 My Chatbot Analytics"):
                show_chat_analytics(st.session_state.user_id)

        elif choice == "Nutrition":
            nutrition_chat(st.session_state.user_id)

        elif choice == "Report":
            # Generate PDF Report button
            if st.button("📄 Generate PDF Report"):
                path = generate_user_report(
                    st.session_state.user_id,
                    st.session_state.user['name']
                )
                # Provide download button for the generated report
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download", f, file_name=path, mime="application/pdf")

if __name__ == "__main__":
    main()