import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import plotly.express as px

# Function to save user data in their folder
def save_data(username, phone, dob, email, password):
    user_folder = os.path.join("users", username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    user_data = {
        "Username": username,
        "Phone": phone,
        "DOB": dob.strftime('%Y-%m-%d'),
        "Email": email,
        "Password": password
    }
    json_file_path = os.path.join(user_folder, "Credentials.json")
    with open(json_file_path, "w") as json_file:
        json.dump(user_data, json_file)

# Function to verify login
def verify_login(username, password):
    user_folder = os.path.join("users", username)
    json_file_path = os.path.join(user_folder, "Credentials.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            user_data = json.load(json_file)
            if user_data.get("Password") == password:
                return True
    return False

# Function to save marks in the user's folder as a CSV file
def save_marks(username, marks):
    user_folder = os.path.join("users", username)
    marks_file_path = os.path.join(user_folder, "marks.csv")

    # Create a DataFrame from marks
    marks_df = pd.DataFrame([marks])

    # Save the marks as a new CSV if it doesn't exist
    if not os.path.exists(marks_file_path):
        marks_df.to_csv(marks_file_path, index=False)

# Function to check if marks are already submitted
def marks_exist(username):
    user_folder = os.path.join("users", username)
    marks_file_path = os.path.join(user_folder, "marks.csv")
    return os.path.exists(marks_file_path)

# Function to calculate average marks for each subject
def calculate_average_marks(marks_df):
    return marks_df.mean()

# Plot different graphs using Plotly
def plot_graphs(marks_df):
    st.subheader("Average Marks (Bar Chart)")
    avg_marks = calculate_average_marks(marks_df)
    bar_fig = px.bar(avg_marks, x=avg_marks.index, y=avg_marks.values, labels={'x': 'Subjects', 'y': 'Average Marks'})
    st.plotly_chart(bar_fig)

    st.subheader("Marks Per Subject (Line Graph)")
    marks_sequence = marks_df.melt(var_name='Subject', value_name='Marks')
    line_fig = px.line(marks_sequence, x='Subject', y='Marks', title='Marks Per Subject (Continuous)')
    st.plotly_chart(line_fig)

    st.subheader("Marks Distribution (Pie Chart)")
    latest_marks = marks_df.iloc[-1]  # Get the latest marks
    pie_fig = px.pie(values=latest_marks.values, names=latest_marks.index, title='Marks Distribution for Last Submission')
    st.plotly_chart(pie_fig)

# Setup Streamlit interface
min_date = datetime(1960, 1, 1)

if 'username' in st.session_state:
    st.title(f"Welcome, {st.session_state['username']}!")

    # Check if marks already exist for the logged-in user
    if marks_exist(st.session_state['username']):
        st.success("You have already submitted your marks.")
        
        # Load the user's marks CSV for analysis
        user_folder = os.path.join("users", st.session_state['username'])
        marks_file_path = os.path.join(user_folder, "marks.csv")
        marks_df = pd.read_csv(marks_file_path)

        st.write("Your submitted marks:")
        st.write(marks_df)

        # Plot graphs
        plot_graphs(marks_df)

    else:
        st.subheader("Submit Your Marks")
        subjects = ["FOML", "AAI", "VCC", "BDMS", "DHV"]

        # Dictionary to store selected marks
        marks = {}
        for subject in subjects:
            marks[subject] = st.slider(f"Select marks for {subject}", 0, 100, 50)

        if st.button("Submit Marks"):
            # Save the marks in the CSV file in the user's folder
            save_marks(st.session_state['username'], marks)
            st.success("Marks submitted successfully!")

            # Reload the page after submission to reflect that marks have been submitted

    if st.button("Sign Out"):
        del st.session_state['username']
        st.success("You have been signed out.")

else:
    # Displaying only the selected option in the sidebar
    menu = st.sidebar.selectbox("Select", ["Login", "Signup"])

    if menu == "Signup":
        st.header("Signup Page")
        username = st.text_input("Enter Username:")
        phone = st.text_input("Enter Phone Number:")
        dob = st.date_input("Enter Date of Birth", min_value=min_date)
        email = st.text_input("Enter Email:")
        password = st.text_input("Enter Password:", type="password")

        if st.button("Signup"):
            if not username or not phone or not dob or not email or not password:
                st.error("All fields are required")
            else:
                save_data(username, phone, dob, email, password)
                st.session_state["username"] = username
                st.success(f"Signup successful for {username}!")

    elif menu == "Login":
        st.header("Login Page")
        username = st.text_input("Enter Username:")
        password = st.text_input("Enter Password:", type="password")

        if st.button("Login"):
            if not username or not password:
                st.error("All fields are required")
            elif verify_login(username, password):
                st.session_state["username"] = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid Username or Password.")
