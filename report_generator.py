import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from db import query_db

def generate_user_report(user_id, user_name):
    """
    Generates a personalized PDF fitness report for the user.
    
    Args:
        user_id (int): The ID of the user.
        user_name (str): The name of the user.
    
    Returns:
        str: The file path to the generated PDF.
    """
    # Define the output file path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Fitness_Report_{user_name}_{timestamp}.pdf"
    filepath = os.path.join("reports", filename)

    # Ensure the 'reports' directory exists
    os.makedirs("reports", exist_ok=True)

    # Fetch user data
    user_data = query_db("SELECT * FROM users WHERE id = ?", (user_id,), fetchone=True)
    if not user_data:
        raise ValueError("User not found")

    # Calculate BMI
    height_m = user_data['height'] / 100 if user_data['height'] else 0
    bmi = round(user_data['weight'] / (height_m ** 2), 2) if height_m > 0 else 0

    # Fetch goals
    goals = query_db("SELECT * FROM goals WHERE user_id = ?", (user_id,))

    # Fetch recent workouts (last 14 days)
    workouts = query_db(
        "SELECT date, exercise, duration, calories_burned FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 20",
        (user_id,)
    )

    # Fetch recent chat logs (last 10)
    chat_logs = query_db(
        "SELECT user_message, bot_reply, timestamp FROM chat_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10",
        (user_id,)
    )

    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("🏋️ Fitness Assistant – Personalized Report", title_style))
    story.append(Paragraph(f"Prepared for: <b>{user_name}</b>", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # --- Section: User Profile & BMI ---
    story.append(Paragraph("👤 User Profile & BMI", styles['Heading2']))
    profile_data = [
        ["Name", user_data['name']],
        ["Age", str(user_data['age']) if user_data['age'] else "N/A"],
        ["Gender", user_data['gender'] or "N/A"],
        ["Height", f"{user_data['height']} cm" if user_data['height'] else "N/A"],
        ["Weight", f"{user_data['weight']} kg" if user_data['weight'] else "N/A"],
        ["BMI", f"{bmi} ({get_bmi_category(bmi)})" if bmi > 0 else "N/A"]
    ]
    profile_table = Table(profile_data, colWidths=[2*inch, 3*inch])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 0.2 * inch))

    # --- Section: Fitness Goals ---
    story.append(Paragraph("🎯 Fitness Goals", styles['Heading2']))
    if goals:
        goal_data = [["Goal Type", "Target", "Current", "Status", "Period"]]
        for g in goals:
            period = f"{g['start_date']} → {g['end_date']}" if g['start_date'] and g['end_date'] else "N/A"
            goal_data.append([
                g['goal_type'].replace('_', ' ').title(),
                str(g['target_value']),
                str(g['current_value']),
                g['status'].title(),
                period
            ])
        goal_table = Table(goal_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 2*inch])
        goal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(goal_table)
    else:
        story.append(Paragraph("No goals have been set yet.", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # --- Section: Workout History ---
    story.append(Paragraph("🏋️ Recent Workouts", styles['Heading2']))
    if workouts:
        workout_data = [["Date", "Exercise", "Duration (min)", "Calories"]]
        for w in workouts:
            workout_data.append([
                w['date'],
                w['exercise'],
                str(w['duration']),
                f"{w['calories_burned']:.0f}" if w['calories_burned'] else "N/A"
            ])
        workout_table = Table(workout_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 1.2*inch])
        workout_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(workout_table)
    else:
        story.append(Paragraph("No workouts logged yet.", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # --- Section: Chat Summary ---
    story.append(Paragraph("💬 Chat Summary (Last 10 Interactions)", styles['Heading2']))
    if chat_logs:
        for log in chat_logs:
            story.append(Paragraph(f"<b>You:</b> {log['user_message']}", styles['Normal']))
            story.append(Paragraph(f"<b>Nova AI:</b> {log['bot_reply']}", styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
    else:
        story.append(Paragraph("No chat history found.", styles['Normal']))

    # Build the PDF
    doc.build(story)
    return filepath

def get_bmi_category(bmi):
    """Returns BMI category text for display in the report."""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"