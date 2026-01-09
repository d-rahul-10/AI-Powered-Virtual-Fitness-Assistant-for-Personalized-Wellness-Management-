import streamlit as st
from groq import Groq
from db import query_db, execute_db
import json
import re # For parsing goals from messages

# Initialize the Groq client using the API key from environment variables
client = Groq()

def extract_goals_from_message(user_message):
    """
    Attempts to extract goal information from the user's message using regex.
    This is a basic example, can be enhanced with NLP.
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

def log_chat_interaction(user_id, user_message, bot_reply):
    """Logs the chat interaction to the database."""
    execute_db(
        "INSERT INTO chat_logs (user_id, user_message, bot_reply) VALUES (?, ?, ?)",
        (user_id, user_message, bot_reply)
    )

def get_user_context(user_id):
    """Fetches relevant user data to provide context to the AI."""
    # Fetch user profile
    user_data = query_db("SELECT * FROM users WHERE id = ?", (user_id,), fetchone=True)
    if not user_data:
        return "User data not found."

    # Fetch active goals
    goals = query_db("SELECT goal_type, target_value, current_value, status FROM goals WHERE user_id = ? AND status != 'completed'", (user_id,))
    # Fetch recent workout (last 3 days or similar)
    # Note: SQLite date handling might require specific syntax, adjust if needed
    recent_workouts = query_db(
        "SELECT date, exercise, duration, calories_burned FROM workouts WHERE user_id = ? AND date >= date('now', '-3 days') ORDER BY date DESC LIMIT 3",
        (user_id,)
    )

    context = f"""
    User Profile:
    - Name: {user_data['name']}
    - Age: {user_data['age']}
    - Gender: {user_data['gender']}
    - Height: {user_data['height']} cm
    - Weight: {user_data['weight']} kg

    Active Goals:
    """
    if goals:
        for goal in goals:
            context += f"- Type: {goal['goal_type']}, Target: {goal['target_value']}, Current: {goal['current_value']}, Status: {goal['status']}\n"
    else:
        context += "No active goals.\n"

    context += "\nRecent Workouts (last 3 days):\n"
    if recent_workouts:
        for workout in recent_workouts:
            context += f"- Date: {workout['date']}, Exercise: {workout['exercise']}, Duration: {workout['duration']} min, Calories: {workout['calories_burned']}\n"
    else:
        context += "No recent workouts logged.\n"

    return context

def fitness_chatbot(user_id):
    """Displays the chatbot interface and handles interactions."""
    st.subheader("🤖 Nova AI Fitness Assistant")

    # Initialize session state for chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about fitness, nutrition, or your goals..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get user context
        user_context = get_user_context(user_id)

        # Prepare the full prompt for the AI, including user context
        full_prompt = f"""
        User Context:
        {user_context}

        User Message:
        {prompt}

        Please provide a helpful, friendly, and accurate response related to fitness, nutrition, or the user's goals based on the context provided.
        If the user mentions a goal (e.g., losing weight, gaining muscle, specific exercise targets), acknowledge it and offer relevant advice or encouragement.
        If the user's message seems to define a new goal, please acknowledge it and suggest they might want to formally set it in the Goals section.
        """

        # Add the AI's system context message to the history for the model's reference in subsequent turns
        # (This is optional depending on how you want the conversation to flow, Groq models might handle context differently)
        # st.session_state.messages.append({"role": "system", "content": user_context})

        # Get AI response using Groq
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Nova, a friendly and knowledgeable AI fitness and nutrition assistant. Provide helpful, encouraging, and scientifically-backed advice. Use the user's context (profile, goals, recent workouts) provided to personalize your responses."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                model="llama-3.1-8b-instant", # Updated model name to avoid deprecation error
            )

            response_text = chat_completion.choices[0].message.content

        except Exception as e:
            st.error(f"Error calling Groq API: {e}")
            response_text = "Sorry, I couldn't process your request at the moment. Please try again later."

        # Add AI response to history
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Log the interaction to the database
        log_chat_interaction(user_id, prompt, response_text)

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response_text)

def show_chat_analytics(user_id):
    """Displays basic analytics related to the user's chat history."""
    st.subheader("Chat Analytics")

    # Example: Fetch total number of chats
    # query_db with fetchone=True returns a sqlite3.Row object or None
    # The Row object can be accessed by column name: result['count']
    total_chats_row = query_db("SELECT COUNT(*) as count FROM chat_logs WHERE user_id = ?", (user_id,), fetchone=True)
    # Correctly access the 'count' column from the Row object
    total_count = total_chats_row['count'] if total_chats_row else 0

    # Example: Fetch recent chat logs (last 5)
    recent_logs = query_db(
        "SELECT user_message, bot_reply, timestamp FROM chat_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    )

    st.metric(label="Total Chats", value=total_count)
    if recent_logs:
        st.write("**Recent Interactions:**")
        for log in recent_logs:
            with st.expander(f"Q: {log['user_message'][:50]}..."): # Show first 50 chars of question
                st.write(f"**You:** {log['user_message']}")
                st.write(f"**Nova AI:** {log['bot_reply']}")
                st.caption(f"Timestamp: {log['timestamp']}")
    else:
        st.info("No chat history found yet.")
