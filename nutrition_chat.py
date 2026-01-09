import streamlit as st
from groq import Groq
from db import query_db, execute_db
import tempfile
import os
import fitz  # PyMuPDF for PDF text extraction
from dotenv import load_dotenv

# Load environment variables and initialize Groq client
load_dotenv()
client = Groq()

def extract_text_from_pdf(uploaded_file):
    """Extracts text content from an uploaded PDF file using PyMuPDF."""
    text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        doc = fitz.open(temp_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        os.unlink(temp_path)

    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return ""

    return text

def log_nutrition_chat_interaction(user_id, user_message, bot_reply):
    """Logs the nutrition chat interaction to the database."""
    execute_db(
        "INSERT INTO chat_logs (user_id, user_message, bot_reply) VALUES (?, ?, ?)",
        (user_id, user_message, bot_reply)
    )

def get_user_context(user_id):
    """Fetches relevant user data to provide context to the AI."""
    user_data = query_db("SELECT * FROM users WHERE id = ?", (user_id,), fetchone=True)
    if not user_data:
        return "User data not found."

    goals = query_db("SELECT goal_type, target_value, current_value, status FROM goals WHERE user_id = ? AND status != 'completed'", (user_id,))

    context = f"""
    User Profile:
    - Name: {user_data['name']}
    - Age: {user_data['age']}
    - Gender: {user_data['gender']}
    - Height: {user_data['height']} cm
    - Weight: {user_data['weight']} kg
    - BMI: {user_data['weight'] / ((user_data['height'] / 100) ** 2):.2f}

    Active Goals:
    """
    if goals:
        for goal in goals:
            context += f"- Type: {goal['goal_type']}, Target: {goal['target_value']}, Current: {goal['current_value']}, Status: {goal['status']}\n"
    else:
        context += "No active goals.\n"

    return context

def nutrition_chat(user_id):
    """Displays the nutrition chat interface and handles interactions."""
    st.subheader("🥗 Nutrition Assistant (Nova AI)")

    if f"nutrition_messages_{user_id}" not in st.session_state:
        st.session_state[f"nutrition_messages_{user_id}"] = []

    for message in st.session_state[f"nutrition_messages_{user_id}"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded_file = st.file_uploader("Upload your meal plan (PDF or Text)", type=['pdf', 'txt'])

    if prompt := st.chat_input("Ask about your nutrition, meal plan, calories, macros, etc."):
        st.session_state[f"nutrition_messages_{user_id}"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        user_context = get_user_context(user_id)

        file_content = ""
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                file_content = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                file_content = uploaded_file.getvalue().decode("utf-8")
            else:
                st.error("Unsupported file type. Please upload a PDF or TXT file.")
                return

        full_prompt = f"""
        User Context:
        {user_context}

        Meal Plan Content (if uploaded):
        {file_content}

        User Message:
        {prompt}

        Please provide a helpful, friendly, and accurate response related to nutrition, diet, calories, macros, or meal planning based on the user's context and the meal plan content (if provided).
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Nova, a friendly and knowledgeable AI nutrition assistant. Provide helpful, encouraging, and scientifically-backed advice on nutrition, diet, calories, and meal planning. Use the user's context (profile, goals) and the provided meal plan content (if any) to personalize your responses."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                model="llama-3.1-8b-instant",  # ✅ FIXED: Updated to supported model
            )

            response_text = chat_completion.choices[0].message.content

        except Exception as e:
            st.error(f"Error calling Groq API: {e}")
            response_text = "Sorry, I couldn't process your request at the moment. Please try again later."

        st.session_state[f"nutrition_messages_{user_id}"].append({"role": "assistant", "content": response_text})
        log_nutrition_chat_interaction(user_id, prompt, response_text)
        with st.chat_message("assistant"):
            st.markdown(response_text)