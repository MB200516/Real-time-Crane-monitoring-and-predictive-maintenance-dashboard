import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime, timedelta
import random
import uuid
from playsound import playsound
import folium
from streamlit_folium import folium_static
from pymongo import MongoClient
import os
from email.message import EmailMessage
import smtplib
from twilio.rest import Client



st.set_page_config(
    page_title="Crane Monitoring Dashboard",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
        
        .menu-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f8f9fa;
            padding: 10px 20px;
            border-radius: 10px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        }
        .menu-left {
            display: flex;
            align-items: center;
        }
        .menu-right {
            display: flex;
            gap: 15px;
        }
        .menu-item {
            display: flex;
            align-items: center;
            gap: 5px;
            background: white;
            padding: 8px 15px;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }
        .menu-item:hover {
            background: #e9ecef;
        }
        .dropdown {
            position: relative;
            display: inline-block;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            right: 0;
            background-color: white;
            min-width: 150px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
            border-radius: 8px;
            z-index: 10;
        }
        .dropdown-content a {
            color: black;
            padding: 10px;
            display: block;
            text-decoration: none;
            border-radius: 8px;
        }
        .dropdown-content a:hover {
            background-color: #f1f1f1;
        }
        .dropdown:hover .dropdown-content {
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# Creating the top menu bar
st.markdown("""
    <div class="menu-bar">
        <div class="menu-left">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg" width="30" height="30">
            <strong style="color: #c00; font-size: 18px; margin-left: 8px;">DYNAMIC</strong>
        </div>
        <div class="menu-right">
            <div class="menu-item">
                <span>🔔</span> Notification
            </div>
            <div class="dropdown">
                <div class="menu-item">
                    <span>👤</span> User_123 ▼
                </div>
                <div class="dropdown-content">
                    <a href="#">Profile</a>
                    <a href="#">Help</a>
                    <a href="#">Logout</a>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .alert { background-color: red; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-top:20px; }
    .ok { background-color: #3ad64e; color: white; padding: 10px; border-radius: 5px; text-align: center;margin-top:20px; }
    
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #e41c3b;
        margin-top: -140px;
        margin-bottom: 5px;
        text-align: center;
    }
    .sub-header {
        font-size: 28px;
        font-weight: bold;
        color: #e41c3b;
        margin-top: -30px;
        margin-bottom: 15px;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        color: #e41c3b;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .map{
        font-size: 24px;
        font-weight: bold;
        color: #e41c3b;
        margin-top:10px;
        margin-bottom:20px;
            }
    
    .metric-card {
        background-color: #EDF1FF;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 14px;
        color: white;
        background-color: #4a86e8;
        padding: 3px 8px;
        border-radius: 5px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1e3a8a;
    }
    .metric-unit {
        font-size: 16px;
        color: #666;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e41c3b;
        color: white;
    }
    
    .sidebar-header {
        font-size: 30px;
        font-weight: bold;
        text-align: center;
        color: #e41c3b;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .stButton > button {
        background-color: #e41c3b;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
    }
    .increase-value {
        color: green;
        font-size: 14px;
    }
    .menuitems{
            background color: #332f2f;
            border: none;
            padding: 12px 20px 12px 20px;
            margin-top:
            }
</style>
""", unsafe_allow_html=True)

 
ACCOUNT_SID = "ACa67e6844ef3099d31f846e2703523ae7"
AUTH_TOKEN = "3cdb1c960b47e2a2af96ae55ebef092a"
TWILIO_PHONE = "+19129159176"  # Your Twilio phone number
TO_PHONE = "+917478108591"  # Receiver's phone number 
    
def send_twilio():
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body="🚨MALFUNCTION DETECTED!!",
        from_=TWILIO_PHONE,
        to=TO_PHONE
    )    
    
def play_siren():
    playsound('siren.mp3')

def generate_crane_data(crane_id, days=30):
    """Generate sample data for a crane"""
    timestamps = [datetime.now() - timedelta(days=i, hours=random.randint(0, 23), minutes=random.randint(0, 59)) for i in range(days)]
    timestamps.sort()
    
    data = {
        'timestamp': timestamps,
        'fuel_consumption': [0.02 + random.uniform(0, 0.03) for _ in range(days)],
        'engine_temperature': [50 + random.uniform(0, 10) for _ in range(days)],
        'vibration_level': [0.09 + random.uniform(0, 0.05) for _ in range(days)],
        'operating_hours': list(np.cumsum([6 + random.uniform(0, 4) for _ in range(days)])),
    }
    
    df = pd.DataFrame(data)
    df['crane_id'] = crane_id
    return df

if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'


if 'crane_data' not in st.session_state:
    st.session_state.crane_data = {}
    cranes = [
        {"id": "crane001", "name": "Tower Crane 1"},
        {"id": "crane002", "name": "Tower Crane 2"},
        {"id": "crane003", "name": "Mobile Crane 1"}
    ]
    
    for crane in cranes:
        st.session_state.crane_data[crane["id"]] = generate_crane_data(crane["id"])


if 'selected_crane' not in st.session_state:
    st.session_state.selected_crane = "crane001"


# Sidebar
with st.sidebar:
    
    st.markdown("<div class='sidebar-header'>MENU</div>", unsafe_allow_html=True)
    
    # Navigation buttons
    if st.button("Dashboard", key="nav_dashboard"):
        st.session_state.page = 'dashboard'
    
    if st.button("Historical Statistics", key="nav_statistics"):
        st.session_state.page = 'statistics'
    
    if st.button("Reports", key="nav_reports"):
        st.session_state.page = 'reports'
    
    if st.button("Self Diagnosis", key="nav_diagnosis"):
        st.session_state.page = 'diagnosis'
    
    if st.button("Messages", key="nav_messages"):
        st.session_state.page = 'messages'
        
       
    
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-header'>Select Crane</div>", unsafe_allow_html=True)
    
    # Crane selector
    crane_options = {
        "crane001": "Tower Crane 1 (crane001)",
        "crane002": "Tower Crane 2 (crane002)",
        "crane003": "Mobile Crane 1 (crane003)"
    }
    
    selected_crane = st.selectbox(
        "Select a crane", 
        options=list(crane_options.keys()),
        format_func=lambda x: crane_options[x],
        key="crane_selector"
    )
    
    st.session_state.selected_crane = selected_crane
    

    # Display current time and date in the bottom of sidebar
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='position: fixed; bottom: 20px; font-size: 0.8rem;'>{datetime.now().strftime('%d-%m-%Y %H:%M')}</div>", unsafe_allow_html=True)
def google_maps_alternative():
    """
    Multiple ways to add maps to Streamlit with crane locations
    """
    
    # Create a map centered on a typical construction area
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    
    # Add markers for crane locations
    crane_locations = {
        "crane001": {"name": "Tower Crane 1", "location": [23.319792,76.554095]},
        "crane002": {"name": "Tower Crane 2", "location": [23.319792,76.554095]},
        "crane003": {"name": "Mobile Crane 1", "location": [23.319792,76.554095]}
    }
    
    # Add a marker for the selected crane
    selected_crane = st.session_state.selected_crane
    selected_location = crane_locations[selected_crane]
    
    folium.Marker(
        location=selected_location["location"],
        popup=selected_location["name"],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Add markers for other cranes with different colors
    for crane_id, crane_info in crane_locations.items():
        if crane_id != selected_crane:
            folium.Marker(
                location=crane_info["location"],
                popup=crane_info["name"],
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
    
    # Display the map
    folium_static(m,height=500,width=2000)
# Main content area

def generate_crane_data(crane_id, days=30):
    """Generate dynamic sample data for a crane with more variability"""
    timestamps = [datetime.now() - timedelta(days=i, hours=random.randint(0, 23), minutes=random.randint(0, 59)) for i in range(days)]
    timestamps.sort()
    
    # Introduce more dynamic and realistic data generation
    base_fuel = random.uniform(0.02, 0.05)
    base_temp = random.uniform(50, 60)
    base_vibration = random.uniform(0.09, 0.15)
    
    data = {
        'timestamp': timestamps,
        'fuel_consumption': [base_fuel + np.sin(i/2) * random.uniform(0, 0.02) for i in range(days)],
        'engine_temperature': [base_temp + np.cos(i/3) * random.uniform(0, 5) for i in range(days)],
        'vibration_level': [base_vibration + np.random.normal(0, 0.01) for _ in range(days)],
        'operating_hours': list(np.cumsum([6 + random.uniform(0, 4) for _ in range(days)]))
    }
    
    df = pd.DataFrame(data)
    df['crane_id'] = crane_id
    return df


def render_dashboard_page():
    selected_id = st.session_state.selected_crane
    crane_name = {"crane001": "Tower Crane 1", "crane002": "Tower Crane 2", "crane003": "Mobile Crane 1"}[selected_id]
    
    # Regenerate data with slight variations on each render
    st.session_state.crane_data[selected_id] = generate_crane_data(selected_id)
    crane_data = st.session_state.crane_data[selected_id]
 
    # Main header
    st.markdown("<div class='main-header'>REAL-TIME MONITORING</div>", unsafe_allow_html=True)
    
   
    
    # Subheader with crane name
    st.markdown(f"<div class='sub-header'>{crane_name} </div>", unsafe_allow_html=True)

  

    # Live Monitoring Section
    st.markdown("<div class='section-header'>Live Monitoring</div>", unsafe_allow_html=True)
   
    
    
    # Current values
    current_fuel = np.random.uniform(18,20)
    current_temp = np.random.uniform(36,42)
    current_vibration = crane_data['vibration_level'].iloc[-1]
    current_hours=0
    for i in range (1000):
        current_hours+=0.000277


    
    # Calculate changes
    fuel_change = round(current_fuel - crane_data['fuel_consumption'].iloc[-2], 2)
    temp_change = round(current_temp - crane_data['engine_temperature'].iloc[-2], 1)
    vibration_change = round(current_vibration - crane_data['vibration_level'].iloc[-2], 2)
    
    # Display metrics in 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Volume</div>
            <div class='metric-value'>{:.2f} <span class='metric-unit'>L</span></div>
            <div class='increase-value'>↑ {:.2f}</div>
        </div>
        """.format(current_fuel, fuel_change), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Engine Temperature</div>
            <div class='metric-value'>{:.2f} <span class='metric-unit'>°C</span></div>
            <div class='increase-value'>↑ {:.1f}</div>
        </div>
        """.format(current_temp, temp_change), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Vibration Level</div>
            <div class='metric-value'>{:.2f} <span class='metric-unit'>mm/s</span></div>
            <div class='increase-value'>↑ {:.2f}</div>
        </div>
        """.format(np.random.uniform(0.01,0.4), vibration_change), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Total Operating Hours</div>
            <div class='metric-value'>{:.1f} <span class='metric-unit'>hrs</span></div>
        </div>
        """.format(current_hours), unsafe_allow_html=True)

    
    if current_fuel <15:
        send_twilio()
        st.markdown('<div class="alert">Low Fuel</div>', unsafe_allow_html=True)
    elif current_temp > 70:
        play_siren()
        st.markdown('<div class="alert">⚠ Overheating Alert! Reduce Load</div>', unsafe_allow_html=True)

    
    elif current_vibration > 2.5:
        st.markdown('<div class="alert">⚠ High Vibration! Possible Damage Risk</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="ok">✅ All Systems Normal</div>', unsafe_allow_html=True)
    
   
    # Performance Trends Section
    st.markdown("<div class='section-header'>Performance Trends</div>", unsafe_allow_html=True)
    
    # Tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["Fuel Consumption", "Temperature", "Vibration", "Operating Hours"])
    
    with tab1:
        fig = px.line(
            crane_data.tail(14), 
            x='timestamp', 
            y='fuel_consumption',
            labels={"timestamp": "Date & Time", "fuel_consumption": "Fuel Consumption (L/min)"},
            title=f"Fuel Consumption Trend for {crane_name}"
        )
        fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=40))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(
            crane_data.tail(14), 
            x='timestamp', 
            y='engine_temperature',
            labels={"timestamp": "Date & Time", "engine_temperature": "Engine Temperature (°C)"},
            title=f"Engine Temperature Trend for {crane_name}"
        )
        fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=40))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.line(
            crane_data.tail(14), 
            x='timestamp', 
            y='vibration_level',
            labels={"timestamp": "Date & Time", "vibration_level": "Vibration Level (mm/s)"},
            title=f"Vibration Level Trend for {crane_name}"
        )
        fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=40))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # For operating hours, we'll show daily increments
        daily_hours = crane_data.copy()
        daily_hours['date'] = daily_hours['timestamp'].dt.date
        daily_hours = daily_hours.groupby('date').agg({'operating_hours': 'max'}).reset_index()
        daily_hours['daily_hours'] = daily_hours['operating_hours'].diff().fillna(daily_hours['operating_hours'])
        
        fig = px.bar(
            daily_hours.tail(14), 
            x='date', 
            y='daily_hours',
            labels={"date": "Date", "daily_hours": "Daily Operating Hours"},
            title=f"Daily Operating Hours for {crane_name}"
        )
        fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=40))
        st.plotly_chart(fig, use_container_width=True)
        
    # Predictive Maintenance Section
    st.markdown("<div class='section-header'>Predictive Maintenance</div>", unsafe_allow_html=True)


    # Generate some maintenance predictions
    maintenance_data = {
        "component": ["Hydraulic System", "Engine", "Structural Components", "Control System"],
        "health_status": ["Good", "Warning", "Good", "Good"],
        "next_maintenance": ["2025-04-15", "2025-03-25", "2025-05-10", "2025-04-30"],
        "priority": ["Low", "High", "Low", "Medium"]
    }
  
    maintenance_df = pd.DataFrame(maintenance_data)  
    
    # Apply conditional formatting
    def highlight_priority(val):
        if val == "High":
            return 'background-color: #ffcccc'
        elif val == "Medium":
            return 'background-color: #ffffcc'
        else:
            return 'background-color: #ccffcc'
    
   
    
    st.dataframe(
        maintenance_df.style.applymap(highlight_priority, subset=['priority']),
        use_container_width=True
    )
    
    st.markdown("<div class='map'>CRANE LOCATION</div>", unsafe_allow_html=True)
    google_maps_alternative()
    time.sleep(2)
    st.rerun()

def render_messages_page():
    client = MongoClient("mongodb://localhost:27017/")  # Update this with your MongoDB connection

    # Create or get the database and collection
    db = client["dynamic-hackathon"]
    messages_collection = db["messages"]
    import streamlit as st
    from datetime import datetime
    
    # Initialize session state for messages if not already exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    def send_message():
        # Check if message is not empty
        if st.session_state.message:
            # Create message dictionary
            new_message = {
                "sender": st.session_state.sender,
                "recipient": st.session_state.recipient,
                "message": st.session_state.message,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add message to session state
            st.session_state.messages.append(new_message)
            
            # Clear the message input
            st.session_state.message = ""
    
    def display_messages():
        st.header("Message History")
        
        # Reverse the messages to show latest first
        for msg in reversed(st.session_state.messages):
            # Create columns to simulate chat-like display
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.write(f"{msg['sender']}")
            
            with col1:
                st.write(msg['message'])
                st.caption(msg['timestamp'])
            
            st.markdown("---")  # Separator between messages
    
    def main():
        st.title("Simple Messaging App")
        
        # User and recipient selection
        col1, col2 = st.columns(2)
        
        with col1:
            sender = st.selectbox("Select Your User", ["Admin"])
            st.session_state.sender = sender
        
        with col2:
            recipient = st.selectbox("Select Recipient", 
                                     [name for name in ["Tower Crane 1 (crane001)", "Tower Crane 2 (crane002)", "Mobile Crane 1 (crane003)"] if name != sender])
            st.session_state.recipient = recipient
        
        # Message input
        st.text_area("Enter your message:", 
                     key="message", 
                     on_change=send_message)
        
        # Display message history
        display_messages()
    
    if name == "main":
        main()

def render_statistics_page():
    selected_id = st.session_state.selected_crane
    crane_name = {"crane001": "Tower Crane 1", "crane002": "Tower Crane 2", "crane003": "Mobile Crane 1"}[selected_id]
    crane_data = st.session_state.crane_data[selected_id]
    
    st.markdown("<div class='main-header'>Historical Statistics</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{crane_name}</div>", unsafe_allow_html=True)
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Filter data based on date range
    filtered_data = crane_data[
        (crane_data['timestamp'].dt.date >= start_date) & 
        (crane_data['timestamp'].dt.date <= end_date)
    ]
    
    if filtered_data.empty:
        st.warning("No data available for the selected date range.")
    else:
        # Summary statistics
        st.markdown("<div class='section-header'>Summary Statistics</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_fuel = filtered_data['fuel_consumption'].mean()
            st.metric("Avg. Fuel Consumption", f"{avg_fuel:.2f} L/Min")
        
        with col2:
            avg_temp = filtered_data['engine_temperature'].mean()
            st.metric("Avg. Engine Temperature", f"{avg_temp:.2f} °C")
        
        with col3:
            avg_vibration = filtered_data['vibration_level'].mean()
            st.metric("Avg. Vibration Level", f"{avg_vibration:.2f} mm/s")
        
        with col4:
            total_hours = filtered_data['operating_hours'].max() - filtered_data['operating_hours'].min()
            st.metric("Total Operating Hours", f"{total_hours:.1f} hrs")
        
        # Detailed charts
        st.markdown("<div class='section-header'>Detailed Analysis</div>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Performance Metrics", "Daily Usage", "Correlation Analysis"])
        
        with tab1:
            # Line charts for all metrics
            metrics = {
                'fuel_consumption': 'Fuel Consumption (L/min)',
                'engine_temperature': 'Engine Temperature (°C)',
                'vibration_level': 'Vibration Level (mm/s)'
            }
            
            for metric, label in metrics.items():
                fig = px.line(
                    filtered_data, 
                    x='timestamp', 
                    y=metric,
                    labels={"timestamp": "Date & Time", metric: label},
                    title=f"{label} Over Time"
                )
                fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=40))
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Daily usage patterns
            daily_data = filtered_data.copy()
            daily_data['date'] = daily_data['timestamp'].dt.date
            daily_data = daily_data.groupby('date').agg({
                'fuel_consumption': 'mean',
                'engine_temperature': 'mean',
                'vibration_level': 'mean',
                'operating_hours': lambda x: x.max() - x.min() if len(x) > 1 else 0
            }).reset_index()
            
            fig = px.bar(
                daily_data, 
                x='date', 
                y='operating_hours',
                labels={"date": "Date", "operating_hours": "Operating Hours"},
                title="Daily Operating Hours"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Correlation analysis
            correlation_data = filtered_data[['fuel_consumption', 'engine_temperature', 'vibration_level']].corr()
            
            fig = px.imshow(
                correlation_data,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                labels=dict(x="Metric", y="Metric", color="Correlation")
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("""
            Interpretation:
            - A correlation close to 1 indicates a strong positive relationship
            - A correlation close to -1 indicates a strong negative relationship
            - A correlation close to 0 indicates little to no relationship
            """)
            


def render_reports_page():
    st.markdown("<div class='main-header'>Reports</div>", unsafe_allow_html=True)
    
    # Report types
    report_types = [
        "Daily Operations Summary",
        "Weekly Performance Analysis",
        "Monthly Maintenance Report",
        "Fuel Efficiency Analysis",
        "Safety Compliance Report",
        "Financial reports"
    ]
    
    # Report selector
    selected_report = st.selectbox("Select Report Type", report_types)
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Generate report button
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            time.sleep(2)  # Simulate processing time
            
            st.success(f"{selected_report} generated successfully for the period {start_date} to {end_date}")
            
            # Sample report content based on type
            if selected_report == "Daily Operations Summary":
                st.markdown("""
                ## Daily Operations Summary
                
                ### Overview
                This report provides a summary of daily crane operations, including operating hours, fuel consumption, and key events.
                
                ### Operating Statistics
                | Date | Operating Hours | Fuel Consumption | Max Load | Events |
                |------|----------------|------------------|----------|--------|
                | 2025-03-19 | 8.2 hrs | 32.8 L | 3.6 tons | None |
                | 2025-03-18 | 7.5 hrs | 30.0 L | 4.2 tons | Maintenance |
                | 2025-03-17 | 9.1 hrs | 36.4 L | 3.8 tons | None |
                
                ### Key Observations
                - Average daily operating time: 8.3 hours
                - Fuel efficiency: 4.0 L/min
                - No safety incidents reported
                """)
            
            elif selected_report == "Monthly Maintenance Report":
                st.markdown("""
                ## Monthly Maintenance Report
                
                ### Maintenance Activities
                | Date | Component | Type | Technician | Hours | Notes |
                |------|-----------|------|------------|-------|-------|
                | 2025-03-15 | Hydraulic System | Preventive | J. Smith | 3.5 | Oil change, filter replacement |
                | 2025-03-08 | Control System | Inspection | T. Johnson | 2.0 | Software update |
                | 2025-03-03 | Engine | Repair | R. Williams | 4.5 | Replaced fuel pump |
                
                ### Upcoming Maintenance
                - Engine oil change: Due in 45 operating hours
                - Structural inspection: Scheduled for 2025-04-10
                - Control system calibration: Due in 120 operating hours
                
                ### Parts Inventory
                - Hydraulic filters: 3 in stock
                - Engine filters: 2 in stock
                - Hydraulic oil: 25 liters in stock
                """)
            elif selected_report=="Financial reports":
                st.markdown("""
                ## Financial Report
                            
                
                ### Servicing Activities
                | Date | Component repaired | Expense | Service Provider |
                |------|-----------|------|------------|
                | 5-03-2025 | Hydraulic System | 6000 | ABC Crane maintenance services |
                | 18-03-2025 | Control System | 8500 | Dynamics crane services |
                | 25-03-2025 | Engine | 10000 | ABC Crane maintenance services |
                | 30-03-2025 | Gearbox | 5500 | PQR Safety solutions |
                | --- | Miscellaneous | 5000|---|

                ### Total expenses: 3500 INR 
                """)
            else:
                st.info(f"Sample content for {selected_report} would appear here.")
            
            # Download option
            st.download_button(
                label="Download Report (PDF)",
                data=b"Sample PDF content",
                file_name=f"{selected_report.replace(' ', '').lower()}{start_date}to{end_date}.pdf",
                mime="application/pdf"
            )

def render_diagnosis_page():
    st.markdown("<div class='main-header'>Self Diagnosis</div>", unsafe_allow_html=True)
    
    # Select crane
    selected_id = st.session_state.selected_crane
    crane_name = {"crane001": "Tower Crane 1", "crane002": "Tower Crane 2", "crane003": "Mobile Crane 1"}[selected_id]
    
    st.markdown(f"<div class='sub-header'>{crane_name} Diagnostics</div>", unsafe_allow_html=True)
    
    # Diagnostic tools
    diagnostic_options = [
        "Full System Check",
        "Engine Diagnostics",
        "Hydraulic System Test",
        "Structural Integrity Check",
        "Control System Diagnostics",
        "Sensor Calibration Test"
    ]
    
    selected_diagnostic = st.selectbox("Select Diagnostic Test", diagnostic_options)
    
    # Run diagnostic button
    if st.button("Run Diagnostic"):
        with st.spinner(f"Running {selected_diagnostic}..."):
            # Simulate progress
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.05)
                progress_bar.progress(i + 1)
            
            # Generate random diagnostic results
            status = random.choice(["Passed", "Warning", "Failed"])
            if status == "Passed":
                st.success(f"{selected_diagnostic} completed: All systems normal")
                icon = "✅"
            elif status == "Warning":
                st.warning(f"{selected_diagnostic} completed: Minor issues detected")
                icon = "⚠"
            else:
                st.error(f"{selected_diagnostic} completed: Critical issues detected") 
                icon = "❌"
            
            # Display detailed results
            st.markdown(f"## {icon} Diagnostic Results")
            
            # Create tabs for different sections of the report
            tab1, tab2, tab3 = st.tabs(["Summary", "Details", "Recommendations"])
            
            with tab1:
                st.markdown(f"""
                ### Diagnostic Summary
                
                Test Performed: {selected_diagnostic}  
                Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
                Overall Status: {status}  
                Technician: Automated System  
                """)
                
                # Sample metrics
                metrics = {
                    "Systems Checked": random.randint(5, 15),
                    "Tests Performed": random.randint(20, 50),
                    "Issues Detected": random.randint(0, 5),
                    "Critical Issues": random.randint(0, 2) if status != "Passed" else 0
                }
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Systems Checked", metrics["Systems Checked"])
                col2.metric("Tests Performed", metrics["Tests Performed"])
                col3.metric("Issues Detected", metrics["Issues Detected"])
                col4.metric("Critical Issues", metrics["Critical Issues"])
            
            with tab2:
                # Create sample test results based on the selected diagnostic
                if selected_diagnostic == "Engine Diagnostics":
                    results = [
                        {"component": "Fuel System", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(0.1, 0.5):.2f} L/min", "threshold": "< 0.3 L/min"},
                        {"component": "Oil Pressure", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(3.0, 5.0):.1f} bar", "threshold": "> 3.5 bar"},
                        {"component": "Temperature", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(50, 70):.1f}°C", "threshold": "< 65°C"},
                        {"component": "Exhaust Emissions", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(10, 30):.1f} ppm", "threshold": "< 25 ppm"}
                    ]
                elif selected_diagnostic == "Hydraulic System Test":
                    results = [
                        {"component": "Hydraulic Pressure", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(150, 210):.1f} bar", "threshold": "180-200 bar"},
                        {"component": "Fluid Level", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(80, 100):.1f}%", "threshold": "> 85%"},
                        {"component": "Fluid Temperature", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(40, 60):.1f}°C", "threshold": "< 55°C"},
                        {"component": "Filter Condition", "status": random.choice(["Passed", "Warning", "Failed"]), "value": f"{random.uniform(70, 100):.1f}%", "threshold": "> 80%"}
                    ]
                else:
                    # Generic results for other tests
                    components = ["Sensor 1", "Sensor 2", "Control Unit", "Safety System", "Power System"]
                    results = [
                        {"component": comp, "status": random.choice(["Passed", "Warning", "Failed"]), 
                         "value": f"{random.uniform(70, 100):.1f}%", "threshold": "> 85%"} 
                        for comp in components
                    ]
                
                # Create DataFrame and display
                results_df = pd.DataFrame(results)
                
                # Apply conditional formatting
                def highlight_status(val):
                    if val == "Passed":
                        return 'background-color: #ccffcc'
                    elif val == "Warning":
                        return 'background-color: #ffffcc'
                    else:
                        return 'background-color: #ffcccc'
                
                st.dataframe(
                    results_df.style.applymap(highlight_status, subset=['status']),
                    use_container_width=True
                )
            
            with tab3:
                # Generate recommendations based on status
                if status == "Passed":
                    st.markdown("""
                    ### Recommendations
                    
                    ✅ All systems are functioning within normal parameters
                    
                    Regular Maintenance:
                    - Continue regular maintenance schedule
                    - Next scheduled maintenance: 2025-04-15
                    """)
                elif status == "Warning":
                    st.markdown("""
                    ### Recommendations
                    
                    ⚠ Some components require attention
                    
                    Recommended Actions:
                    1. Schedule maintenance for flagged components within the next 7 days
                    2. Monitor system performance daily
                    3. Re-run diagnostics after maintenance to verify issues are resolved
                    """)
                else:
                    st.markdown("""
                    ### Recommendations
                    
                    ❌ Immediate attention required
                    
                    Critical Actions:
                    1. SUSPEND OPERATION until issues are resolved
                    2. Contact maintenance team immediately
                    3. Schedule emergency maintenance
                    4. Re-run full diagnostics after repairs
                    
                    Contact Maintenance Team:
                    - Emergency Hotline: 555-123-4567
                    """)

# Display the appropriate page based on session state
if st.session_state.page == 'dashboard':
    render_dashboard_page()
elif st.session_state.page == 'statistics':
    render_statistics_page()
elif st.session_state.page == 'reports':
    render_reports_page()
elif st.session_state.page == 'diagnosis':
    render_diagnosis_page()
elif st.session_state.page=='messages':
    render_messages_page()