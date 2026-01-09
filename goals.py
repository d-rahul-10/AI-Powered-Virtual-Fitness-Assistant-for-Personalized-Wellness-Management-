import streamlit as st
import re # Import the re module for regular expressions
from datetime import datetime, timedelta
from db import query_db, execute_db
from groq import Groq # Import Groq client if goal extraction logic is here

# Initialize the Groq client using the API key from environment variables
# Note: This client initialization might be better placed where it's actually used
# or handled differently if the API key loading isn't working elsewhere.
# For now, keeping it here as it was.
client = Groq()

def extract_goals_from_message(user_message):
    """
    Attempts to extract goal information from the user's message using regex.
    This is a basic example, can be enhanced with NLP or handled in chatbot.py.
    """
    # Example patterns (case-insensitive search)
    patterns = {
        "weight_loss": r"lose\s+(\d+(?:\.\d+)?)\s*(kg|kilograms|lbs|pounds)",
        "weight_gain": r"gain\s+(\d+(?:\.\d+)?)\s*(kg|kilograms|lbs|pounds)",
        "exercise": r"(\d+)\s*(?:minute|minutes|hour|hours)\s+(.*?)\s+per\s+(day|week|month)",
        # Add more patterns as needed
    }

    goals = []
    for goal_type, pattern in patterns.items():
        matches = re.findall(pattern, user_message, re.IGNORECASE)
        for match in matches:
            if goal_type.startswith("weight_"):
                value = float(match[0])
                unit = match[1]
                # Normalize unit to kg for target_value (adjust logic as needed)
                normalized_value = value if unit.lower() in ['kg', 'kilograms'] else value * 0.453592 # lbs to kg
                goals.append({
                    "goal_type": goal_type,
                    "target_value": normalized_value,
                    "description": f"Goal: {user_message}"
                })
            elif goal_type == "exercise":
                duration = int(match[0])
                exercise = match[1]
                frequency = match[2]
                # Example: Store as a text description or define a specific type
                goals.append({
                    "goal_type": "Exercise",
                    "target_value": duration,
                    "description": f"Aim to do {exercise} for {duration} minutes per {frequency}. Extracted from: {user_message}"
                })

    return goals

def set_goal(user_id):
    """Displays the interface for setting a new goal."""
    st.subheader("🎯 Set a New Goal")

    # Option 1: User selects goal type and inputs details
    goal_type = st.selectbox("Goal Type", ["Weight Loss", "Weight Gain", "Exercise", "Other"])
    target_value = st.number_input("Target Value", min_value=0.0, value=0.0, step=0.1)
    start_date = st.date_input("Start Date", value=datetime.today())
    end_date = st.date_input("End Date", value=datetime.today() + timedelta(days=30))

    if st.button("Set Goal"):
        if end_date <= start_date:
            st.error("End date must be after start date.")
        else:
            # Determine internal goal type string (adjust based on your DB schema)
            internal_goal_type = goal_type.lower().replace(" ", "_")

            # Insert the new goal into the database
            result = execute_db(
                "INSERT INTO goals (user_id, goal_type, target_value, current_value, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, internal_goal_type, target_value, 0.0, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 'active') # Default current_value to 0
            )
            if result != -1:
                st.success(f"Goal '{goal_type}' set successfully!")
                st.rerun() # Refresh the view to show the new goal
            else:
                st.error("Failed to set goal. Please try again.")

    # Optional Option 2: Text input to potentially extract goals using AI
    # st.subheader("Or, Describe your goal:")
    # goal_description = st.text_area("Describe your fitness goal (e.g., 'I want to lose 5kg in a month')")
    # if st.button("Extract Goal"):
    #     if goal_description.strip():
    #         extracted_goals = extract_goals_from_message(goal_description)
    #         if extracted_goals:
    #             for goal in extracted_goals:
    #                 # You might want to show a confirmation before inserting
    #                 st.info(f"Potential goal found: {goal['description']}. Type: {goal['goal_type']}, Target: {goal['target_value']}")
    #                 # Insert logic here if confirmed by user
    #                 # result = execute_db(...)
    #                 # if result != -1: st.success(...)
    #         else:
    #             st.warning("No specific goal could be extracted from your description. Please use the form above.")
    #     else:
    #         st.warning("Please enter a goal description.")


def view_goals(user_id):
    """Displays the user's current goals and allows updating status."""
    st.subheader("📋 Your Goals")

    # Fetch goals from the database
    goals = query_db(
        "SELECT id, goal_type, target_value, current_value, start_date, end_date, status FROM goals WHERE user_id = ? ORDER BY start_date DESC",
        (user_id,)
    )

    if not goals:
        st.info("You haven't set any goals yet. Use the 'Set a New Goal' section above.")
        return

    # Display each goal with update options
    for goal in goals:
        col1, col2, col3 = st.columns([2, 1, 1]) # Adjust column ratios as needed
        with col1:
            st.write(f"**{goal['goal_type'].title()}**")
            st.progress(min(goal['current_value'] / goal['target_value'], 1.0)) # Show progress bar
            st.caption(f"Progress: {goal['current_value']:.1f} / {goal['target_value']:.1f}")
        with col2:
            # Update current value (example: for weight loss/gain goals)
            new_current_value = st.number_input(
                f"Update Current Value (ID: {goal['id']})", # Label includes ID for clarity
                value=goal['current_value'],
                min_value=0.0,
                step=0.1,
                key=f"current_val_{goal['id']}" # Unique key for Streamlit widget state
            )
            if st.button(f"Update Value", key=f"update_btn_{goal['id']}"):
                 execute_db(
                    "UPDATE goals SET current_value = ? WHERE id = ?",
                    (new_current_value, goal['id'])
                )
                 st.rerun() # Refresh the view after update
        with col3:
            # Update status (active, completed, etc.)
            new_status = st.selectbox(
                f"Status (ID: {goal['id']})",
                options=["active", "completed", "on hold", "abandoned"],
                index=["active", "completed", "on hold", "abandoned"].index(goal['status']),
                key=f"status_{goal['id']}" # Unique key for Streamlit widget state
            )
            if st.button(f"Update Status", key=f"status_btn_{goal['id']}"):
                execute_db(
                    "UPDATE goals SET status = ? WHERE id = ?",
                    (new_status, goal['id'])
                )
                st.rerun() # Refresh the view after update

        # Display dates
        st.caption(f"Start: {goal['start_date']} | End: {goal['end_date']} | Status: {goal['status']}")
        st.divider() # Add a line between goals
def view_goals(user_id):
    """Displays the user's current goals and allows updating status."""
    st.subheader("📋 Your Goals")

    # Fetch goals from the database
    goals = query_db(
        "SELECT id, goal_type, target_value, current_value, start_date, end_date, status FROM goals WHERE user_id = ? ORDER BY start_date DESC",
        (user_id,)
    )

    if not goals:
        st.info("You haven't set any goals yet. Use the 'Set a New Goal' section above.")
        return

    # Display each goal with update options
    for goal in goals:
        col1, col2, col3 = st.columns([2, 1, 1]) # Adjust column ratios as needed
        with col1:
            st.write(f"**{goal['goal_type'].title()}**")
            # --- FIX: Check for zero target value before division ---
            if goal['target_value'] != 0:
                progress_value = min(goal['current_value'] / goal['target_value'], 1.0)
            else:
                progress_value = 0.0  # If target is 0, progress is 0%
            # ---
            st.progress(progress_value) # Show progress bar
            st.caption(f"Progress: {goal['current_value']:.1f} / {goal['target_value']:.1f}")
        with col2:
            # Update current value (example: for weight loss/gain goals)
            new_current_value = st.number_input(
                f"Update Current Value (ID: {goal['id']})", # Label includes ID for clarity
                value=goal['current_value'],
                min_value=0.0,
                step=0.1,
                key=f"current_val_{goal['id']}" # Unique key for Streamlit widget state
            )
            if st.button(f"Update Value", key=f"update_btn_{goal['id']}"):
                 execute_db(
                    "UPDATE goals SET current_value = ? WHERE id = ?",
                    (new_current_value, goal['id'])
                )
                 st.rerun() # Refresh the view after update
        with col3:
            # Update status (active, completed, etc.)
            new_status = st.selectbox(
                f"Status (ID: {goal['id']})",
                options=["active", "completed", "on hold", "abandoned"],
                index=["active", "completed", "on hold", "abandoned"].index(goal['status']),
                key=f"status_{goal['id']}" # Unique key for Streamlit widget state
            )
            if st.button(f"Update Status", key=f"status_btn_{goal['id']}"):
                execute_db(
                    "UPDATE goals SET status = ? WHERE id = ?",
                    (new_status, goal['id'])
                )
                st.rerun() # Refresh the view after update

        # Display dates
        st.caption(f"Start: {goal['start_date']} | End: {goal['end_date']} | Status: {goal['status']}")
        st.divider() # Add a line between goals