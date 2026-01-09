import streamlit as st
from datetime import datetime
from db import query_db, execute_db

def log_workout(user_id):
    """Displays the interface for logging a new workout."""
    st.subheader("🏋️ Log a Workout")

    # Input fields for workout details
    date = st.date_input("Date", value=datetime.today())
    exercise = st.text_input("Exercise Name (e.g., Running, Push-ups, Yoga)")
    duration = st.number_input("Duration (minutes)", min_value=1, value=30, step=1)
    calories_burned = st.number_input("Calories Burned (optional)", min_value=0.0, value=0.0, step=1.0)

    if st.button("Log Workout"):
        if not exercise.strip():
            st.error("Please enter an exercise name.")
        else:
            # Insert the new workout into the database
            result = execute_db(
                "INSERT INTO workouts (user_id, date, exercise, duration, calories_burned) VALUES (?, ?, ?, ?, ?)",
                (user_id, date.strftime('%Y-%m-%d'), exercise, duration, calories_burned)
            )
            if result != -1:
                st.success(f"Workout '{exercise}' logged successfully!")
                st.rerun() # Refresh the view to potentially show the new workout in the history
            else:
                st.error("Failed to log workout. Please try again.")

def view_workout_history(user_id, limit=10):
    """Fetches and displays the user's recent workout history."""
    st.subheader(f"📋 Workout History (Last {limit} Sessions)")

    # Fetch workouts from the database, ordered by date descending
    workouts = query_db(
        "SELECT date, exercise, duration, calories_burned FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit)
    )

    if not workouts:
        st.info("You haven't logged any workouts yet. Use the 'Log a Workout' section above.")
        return

    # Display each workout in a simple list or table format
    for workout in workouts:
        st.write(f"**Date:** {workout['date']}")
        st.write(f"**Exercise:** {workout['exercise']}")
        st.write(f"**Duration:** {workout['duration']} minutes")
        if workout['calories_burned'] is not None and workout['calories_burned'] > 0:
             st.write(f"**Calories Burned:** {workout['calories_burned']:.0f}")
        else:
            st.write("**Calories Burned:** Not specified")
        st.divider() # Add a line between workouts

# Example usage within the main app flow (called from app.py):
# log_workout(st.session_state.user_id)
# view_workout_history(st.session_state.user_id)