import streamlit as st
import random

def show_tip(user_id):
    """
    Displays a random fitness or nutrition tip to the user.
    This function is designed to be called in the main app (app.py) after login.
    """
    # List of fitness and nutrition tips
    tips = [
        "💧 Stay hydrated! Aim for at least 8 glasses of water per day.",
        "🚶‍♂️ Move more! Try to take a 10-minute walk after every meal.",
        "😴 Prioritize sleep! Aim for 7-9 hours of quality sleep each night.",
        "🥦 Eat your veggies! Fill half your plate with colorful vegetables.",
        "🏋️‍♀️ Consistency beats intensity. Regular, moderate exercise is key.",
        "🍎 Choose whole foods. Opt for fruits, vegetables, whole grains, and lean proteins.",
        "📉 Don't skip breakfast. A healthy morning meal kickstarts your metabolism.",
        "📊 Track your progress. Logging your workouts and meals helps you stay accountable.",
        "🧘‍♂️ Manage stress. Practice deep breathing, meditation, or yoga.",
        "🍽️ Practice mindful eating. Slow down and savor your food.",
        "🧃 Limit sugary drinks. Choose water, unsweetened tea, or sparkling water instead.",
        "💪 Strength train 2-3 times a week. It builds muscle and boosts your metabolism.",
        "📅 Set realistic goals. Break down big goals into smaller, achievable steps.",
        "🔥 Remember: Nutrition is 80% of the fitness equation.",
        "🌟 Celebrate non-scale victories! Improved energy, better sleep, or fitting into old clothes are wins!",
        "🚫 Avoid crash diets. Sustainable lifestyle changes lead to lasting results.",
        "🤝 Consider working with a professional. A certified trainer or dietitian can provide personalized guidance.",
        "📅 Schedule your workouts. Treat them like important appointments.",
        "🥬 Don't fear healthy fats. Avocados, nuts, and olive oil are essential for health.",
        "🎉 You've got this! Every step you take is progress."
    ]

    # Select a random tip
    random_tip = random.choice(tips)

    # Display the tip in a styled container
    st.markdown(
        f"""
        <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #4682B4; margin: 15px 0;'>
            <p style='font-size: 16px; color: #2c3e50; margin: 0;'><strong>💡 Fitness Tip:</strong> {random_tip}</p>
        </div>
        """,
        unsafe_allow_html=True
    )