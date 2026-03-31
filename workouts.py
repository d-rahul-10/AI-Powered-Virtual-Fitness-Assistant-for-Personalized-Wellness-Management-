import streamlit as st
from datetime import datetime
from db import query_db, execute_db

# Common exercise types for the dropdown
EXERCISE_OPTIONS = [
    "Running", "Walking", "Cycling", "Swimming", "Yoga",
    "Weight Training", "HIIT", "Push-ups", "Pull-ups", "Jump Rope",
    "Pilates", "Boxing", "Dancing", "Rowing", "Other"
]


def log_workout(user_id):
    """Displays the interface for logging a new workout."""
    st.subheader("🏋️ Log a Workout")

    with st.form("log_workout_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.today())
            exercise_type = st.selectbox("Exercise Type", EXERCISE_OPTIONS)
            if exercise_type == "Other":
                custom_exercise = st.text_input("Custom Exercise Name")
            else:
                custom_exercise = ""
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, value=30, step=1)
            calories_burned = st.number_input(
                "Calories Burned (optional)", min_value=0.0, value=0.0, step=1.0
            )

        submitted = st.form_submit_button("✅ Log Workout", type="primary", use_container_width=True)

    if submitted:
        exercise = custom_exercise.strip() if exercise_type == "Other" else exercise_type
        if not exercise:
            st.error("Please enter an exercise name.")
        else:
            result = execute_db(
                "INSERT INTO workouts (user_id, date, exercise, duration, calories_burned) VALUES (?, ?, ?, ?, ?)",
                (user_id, date.strftime('%Y-%m-%d'), exercise, duration, calories_burned)
            )
            if result != -1:
                st.success(f"✅ Workout '{exercise}' logged successfully!")
                st.rerun()
            else:
                st.error("Failed to log workout. Please try again.")

    # Always show history below the log form
    st.divider()
    view_workout_history(user_id)


def view_workout_history(user_id, limit=10):
    """Fetches and displays the user's recent workout history as a table."""
    st.subheader(f"📋 Workout History (Last {limit} Sessions)")

    workouts = query_db(
        "SELECT date, exercise, duration, calories_burned "
        "FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit)
    )

    if not workouts:
        st.info("You haven't logged any workouts yet. Use the form above to get started!")
        return

    # Build table data
    rows = []
    for w in workouts:
        cal = f"{w['calories_burned']:.0f}" if w['calories_burned'] else "—"
        rows.append({
            "Date": w['date'],
            "Exercise": w['exercise'],
            "Duration (min)": w['duration'],
            "Calories Burned": cal,
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)
