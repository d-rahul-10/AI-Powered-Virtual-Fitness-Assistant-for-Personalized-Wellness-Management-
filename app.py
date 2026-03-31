import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from auth import register, login
from bmi import show_bmi
from pro import manage_profile
from workouts import log_workout
from tips import show_tip
from dashboard import show_dashboard
from goals import set_goal, view_goals
from report_generator import generate_user_report
from chatbot import fitness_chatbot, show_chat_analytics
from nutrition_chat import nutrition_chat

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fitness Assistant",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

/* Welcome banner */
.welcome-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px 30px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(102,126,234,0.4);
}
.welcome-banner h2 { color: #fff; margin: 0 0 6px; font-size: 1.8rem; }
.welcome-banner p  { color: rgba(255,255,255,0.85); margin: 0; font-size: 1rem; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #f8f9ff;
    border-radius: 12px;
    padding: 14px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
/* Make metric text dark for visibility */
[data-testid="stMetric"] * {
    color: #222 !important;
}
</style>
""", unsafe_allow_html=True)


def main():
    if "user_id" not in st.session_state:
        # ── Auth pages ────────────────────────────────────────────────────────
        page = st.sidebar.selectbox("Menu", ["Login", "Register"])
        if page == "Login":
            login()
        else:
            register()
    else:
        # ── Sidebar ───────────────────────────────────────────────────────────
        try:
            st.sidebar.image("Logo.png", width=120)
        except (FileNotFoundError, Exception):
            st.sidebar.markdown("## 🏋️ Fitness Assistant")

        st.sidebar.markdown(
            f"<div style='font-size:1rem; padding:6px 0;'>👋 Hello, "
            f"<b>{st.session_state.user['name']}</b></div>",
            unsafe_allow_html=True,
        )
        st.sidebar.divider()

        choice = st.sidebar.radio(
            "📂 Navigation",
            ["🏠 Dashboard", "📏 BMI", "👤 Profile", "🏋️ Workout",
             "🎯 Goals", "🤖 Chatbot", "🥗 Nutrition", "📄 Report", "🚪 Logout"],
        )
        st.sidebar.divider()
        show_tip(st.session_state.user_id)

        # ── Welcome banner ────────────────────────────────────────────────────
        st.markdown(
            f"""
            <div class='welcome-banner'>
                <h2>🏋️ Fitness Assistant</h2>
                <p>AI-powered fitness insights for <b>{st.session_state.user['name']}</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Routing ───────────────────────────────────────────────────────────
        if choice == "🚪 Logout":
            st.warning("Are you sure you want to logout?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Logout"):
                    st.session_state.clear()
                    st.rerun()
            with col2:
                if st.button("No, Stay"):
                    st.rerun()

        elif choice == "🏠 Dashboard":
            show_dashboard(st.session_state.user_id)

        elif choice == "📏 BMI":
            show_bmi(st.session_state.user)

        elif choice == "👤 Profile":
            manage_profile(st.session_state.user_id)

        elif choice == "🏋️ Workout":
            log_workout(st.session_state.user_id)

        elif choice == "🎯 Goals":
            set_goal(st.session_state.user_id)
            st.divider()
            view_goals(st.session_state.user_id)

        elif choice == "🤖 Chatbot":
            fitness_chatbot(st.session_state.user_id)
            with st.expander("📊 My Chat Analytics"):
                show_chat_analytics(st.session_state.user_id)

        elif choice == "🥗 Nutrition":
            nutrition_chat(st.session_state.user_id)

        elif choice == "📄 Report":
            st.subheader("📄 Generate Your Fitness Report")
            st.write("Download a personalised PDF summary of your profile, goals, workouts, and chat history.")
            if st.button("📥 Generate PDF Report", type="primary"):
                try:
                    path = generate_user_report(
                        st.session_state.user_id,
                        st.session_state.user['name'],
                        max_workout_entries=5,
                        max_goal_entries=5,
                        max_chat_entries=5
                    )
                    with open(path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Report",
                            f,
                            file_name=path,
                            mime="application/pdf",
                            type="primary",
                        )
                    st.success("Report generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate report: {e}")


if __name__ == "__main__":
    main()
