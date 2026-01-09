import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from db import query_db
from datetime import datetime, timedelta
import calendar

def show_dashboard(user_id):
    """Displays the user's fitness dashboard."""
    st.subheader("📊 Dashboard")

    # Fetch user profile data
    user_data = query_db("SELECT * FROM users WHERE id = ?", (user_id,), fetchone=True)
    if not user_data:
        st.error("User data not found. Please log in again.")
        st.session_state.clear()
        st.rerun()
        return

    # Fetch user's goals
    goals = query_db("SELECT goal_type, target_value, current_value, status FROM goals WHERE user_id = ?", (user_id,))

    # Fetch user's recent workouts (last 7 days)
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    workouts = query_db(
        "SELECT date, exercise, duration, calories_burned FROM workouts WHERE user_id = ? AND date >= ? ORDER BY date DESC",
        (user_id, seven_days_ago)
    )

    # Fetch user's chat logs (last 7 days)
    chat_logs = query_db(
        "SELECT timestamp, user_message FROM chat_logs WHERE user_id = ? AND timestamp >= ? ORDER BY timestamp DESC",
        (user_id, seven_days_ago)
    )

    # Calculate key metrics
    total_workouts = len(workouts)
    total_calories_burned = sum(w['calories_burned'] for w in workouts if w['calories_burned']) if workouts else 0
    active_goals = len([g for g in goals if g['status'] != 'completed'])
    total_goals = len(goals)

    # --- Display Key Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Workouts", total_workouts)
    col2.metric("Calories Burned (Last 7 Days)", f"{total_calories_burned:.0f}")
    col3.metric("Active Goals", f"{active_goals}/{total_goals}")
    col4.metric("BMI", round(user_data['weight'] / ((user_data['height'] / 100) ** 2), 2)) # Recalculate BMI


    # --- Goal Progress Chart ---
    if goals:
        st.subheader("🎯 Goal Progress")
        goal_names = [g['goal_type'] for g in goals]
        current_values = [g['current_value'] for g in goals]
        target_values = [g['target_value'] for g in goals]
        statuses = [g['status'] for g in goals]

        # Create a combined bar chart for current vs target
        fig_goals = go.Figure(data=[
            go.Bar(name='Current Value', x=goal_names, y=current_values, marker_color='lightblue'),
            go.Bar(name='Target Value', x=goal_names, y=target_values, marker_color='orange')
        ])
        fig_goals.update_layout(
            title="Current vs Target Values for Goals",
            xaxis_title="Goal Type",
            yaxis_title="Value",
            barmode='group'
        )
        st.plotly_chart(fig_goals, use_container_width=True)

        # Status pie chart
        status_counts = {status: statuses.count(status) for status in set(statuses)}
        fig_status = px.pie(
            names=list(status_counts.keys()),
            values=list(status_counts.values()),
            title="Goal Status Distribution"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("You haven't set any goals yet. Go to the 'Goals' section to get started!")


    # --- Workout Activity Chart ---
    if workouts:
        st.subheader("🏋️ Recent Workout Activity")
        workout_dates = [w['date'] for w in workouts]
        workout_durations = [w['duration'] for w in workouts]
        workout_calories = [w['calories_burned'] for w in workouts]

        # Prepare data for plotting (sum calories/duration per date if multiple workouts per day)
        daily_stats = {}
        for w in workouts:
            date = w['date']
            if date not in daily_stats:
                daily_stats[date] = {'duration': 0, 'calories': 0}
            daily_stats[date]['duration'] += w['duration']
            daily_stats[date]['calories'] += w['calories_burned']

        sorted_dates = sorted(daily_stats.keys())
        durations = [daily_stats[date]['duration'] for date in sorted_dates]
        calories = [daily_stats[date]['calories'] for date in sorted_dates]

        fig_workouts = go.Figure()
        fig_workouts.add_trace(go.Scatter(x=sorted_dates, y=durations, mode='lines+markers', name='Duration (min)', yaxis='y1'))
        fig_workouts.add_trace(go.Scatter(x=sorted_dates, y=calories, mode='lines+markers', name='Calories Burned', yaxis='y2'))

        fig_workouts.update_layout(
            title="Workout Duration & Calories Burned (Last 7 Days)",
            xaxis_title="Date",
            yaxis=dict(title="Duration (minutes)", side='left'),
            yaxis2=dict(title="Calories", side='right', overlaying='y'),
        )
        st.plotly_chart(fig_workouts, use_container_width=True)
    else:
        st.info("No recent workout data found. Log some workouts in the 'Workout' section.")


    # --- Chat Activity Chart ---
    if chat_logs:
        st.subheader("💬 Chat Activity (Last 7 Days)")
        # Extract dates from timestamps
        log_dates = [datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')).date() for log in chat_logs]
        # Count messages per day
        date_counts = {}
        for date in log_dates:
            date_counts[date] = date_counts.get(date, 0) + 1

        # Prepare data for bar chart
        sorted_log_dates = sorted(date_counts.keys())
        message_counts = [date_counts[date] for date in sorted_log_dates]

        fig_chat = px.bar(
            x=[date.strftime('%Y-%m-%d') for date in sorted_log_dates], # Format dates for x-axis
            y=message_counts,
            labels={'x': 'Date', 'y': 'Number of Messages'},
            title="Number of Messages per Day"
        )
        st.plotly_chart(fig_chat, use_container_width=True)
    else:
        st.info("No recent chat activity found. Start a conversation with Nova AI!")
