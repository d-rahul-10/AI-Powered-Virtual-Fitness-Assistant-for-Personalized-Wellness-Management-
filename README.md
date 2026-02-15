🏋️ FitNova AI – Your Personal AI Fitness & Nutrition Coach
FitNova AI is an intelligent, privacy-first fitness assistant that delivers personalized workout plans, nutrition advice, and motivational coaching—all through a conversational AI interface. Built with Streamlit, SQLite, and Groq’s ultra-fast LLMs, it runs locally on your machine with no cloud dependencies for your health data.

💡 No wearables. No subscriptions. No generic advice.
Just a smart, contextual AI coach who knows your goals, your progress, and your journey.

✨ Features
🔐 Secure Local Storage: All your data (profile, workouts, goals, chats) stays in a local SQLite database—never uploaded to the cloud.
🤖 Context-Aware AI Coach ("Nova AI"): Uses your real data (BMI, goals, recent workouts) to give truly personalized advice—not generic tips.
🥗 Nutrition Analysis: Upload PDF/text meal plans and ask questions like “Is this high in protein?” or “How many calories?”
📊 Interactive Dashboard: Visualize your progress with Plotly charts for goals, workouts, and activity trends.
📄 One-Click PDF Reports: Generate and download a professional summary of your fitness journey.
⚡ Blazing Fast AI: Powered by Groq’s llama-3.1-8b-instant (sub-2-second responses).
🌐 Zero Setup Database: Uses SQLite—no MySQL server needed!
🛡️ Privacy by Design: Only stateless prompts are sent to Groq; your personal data never leaves your device.
🚀 Quick Start
Prerequisites
Python 3.8+
A Groq API Key (free tier available)
Installation
bash
# Clone the repo
git clone (https://github.com/d-rahul-10/AI-Powered-Virtual-Fitness-Assistant-for-Personalized-Wellness-Management-)
cd FitNova-AI

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up your API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Initialize the database
python init_db.py

# Run the app
streamlit run app.py🧠 How It Works
You log in and enter your profile (height, weight, goals).
FitNova stores everything locally in Fitness Assistant.db.
When you chat with Nova AI, the system:
Fetches your BMI, active goals, and recent workouts from the local DB.
Injects this context into the prompt sent to Groq.
Returns personalized, relevant advice in <2 seconds.
All interactions are logged locally for continuity and reporting.
🔄 No model training. No data collection. Just smart use of off-the-shelf AI + your own data.

📂 Project Structure
FitNova-AI/
├── .env                 
├── requirements.txt   
├── init_db.py          
├── app.py              
├── db.py               
├── auth.py              
├── chatbot.py           
├── nutrition_chat.py    
├── dashboard.py         

⚠️ Important Notes
Model Update: This project uses llama-3.1-8b-instant, the official replacement for the deprecated llama3-8b-8192 (shut down by Groq on August 30, 2025).
Privacy: Your health data is never sent to Groq—only anonymized, stateless prompts.
Local-First: Designed for single-user, offline-capable use (except for AI calls).
🤝 Contributing
Contributions are welcome! Please open an issue or submit a PR for:

Bug fixes
New features (e.g., voice input, wearable integration)
UI improvements
