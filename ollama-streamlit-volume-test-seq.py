import os
import tempfile
import pandas as pd
import streamlit as st
import random
import time
import json
import requests

# Create a temporary directory for storing the uploaded files
temp_dir = tempfile.TemporaryDirectory()

# Function to validate the uploaded file
def validate_file(file):
    try:
        # Read the file using pandas
        df = pd.read_excel(file)
        return True, df.shape[0]
    except Exception as e:
        return False, 0

# Function to chat with the Llama3 model
def chat(messages):
    model = "llama3:8B"
    r = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
    )
    r.raise_for_status()
    output = ""
    message = {}  # Initialize the message variable

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content

        if body.get("done", False):
            message["content"] = output
            return message


error_log = []

# Sidebar for file uploads
st.sidebar.title("Upload Files")
users_file = st.sidebar.file_uploader("Choose a file with user details", type=["xlsx", "xls"])
questions_file = st.sidebar.file_uploader("Choose a file with questions", type=["xlsx", "xls"])

# Display the number of records in each file
if users_file is not None:
    is_users_valid, user_count = validate_file(users_file)
    if is_users_valid:
        st.sidebar.write(f"Number of records in the user details file: {user_count}")
    else:
        st.sidebar.error("The user details file is not a valid Excel file.")

if questions_file is not None:
    is_questions_valid, question_count = validate_file(questions_file)
    if is_questions_valid:
        st.sidebar.write(f"Number of records in the questions file: {question_count}")
    else:
        st.sidebar.error("The questions file is not a valid Excel file.")

# Add a "Run Volume Test" button
run_button = st.sidebar.button("Run Volume Test", disabled=(users_file is None or questions_file is None))

# Main content area
st.title("Volume Testing Simulator")

if run_button:
    if users_file is not None and questions_file is not None:
        # Save the uploaded files to the temporary directory
        users_file_path = os.path.join(temp_dir.name, users_file.name)
        with open(users_file_path, "wb") as f:
            f.write(users_file.getbuffer())

        questions_file_path = os.path.join(temp_dir.name, questions_file.name)
        with open(questions_file_path, "wb") as f:
            f.write(questions_file.getbuffer())

        # Validate the files
        is_users_valid, user_count = validate_file(users_file_path)
        is_questions_valid, question_count = validate_file(questions_file_path)

        if is_users_valid and is_questions_valid:
            # Read the user details and questions from the files
            users = pd.read_excel(users_file_path)
            questions = pd.read_excel(questions_file_path)["Question"].tolist()

            # Progress bar
            progress_bar = st.progress(0)
            # Text to display current progress
            progress_text = st.empty()

            # Simulate volume testing
            # Simulate volume testing
            for user_id in users.index:
                messages = []
                random.shuffle(questions)  # Shuffle the questions for each user
                for i, question in enumerate(questions):
                    try:
                        messages.append({"role": "user", "content": question})
                        # Create placeholders for the question and answer
                        question_placeholder = st.empty()
                        answer_placeholder = st.empty()
                        # Display the question right away
                        question_placeholder.write(f"User {user_id}: {question}")
                        # Display a waiting indicator while waiting for the answer from the model
                        with st.spinner('Waiting for the answer...'):
                            response = chat(messages)
                            answer = response["content"]
                            # Update the answer placeholder with the answer
                            answer_placeholder.write(f"LLaMA 8B: {answer}")
                        # Erase the question and answer
                        question_placeholder.empty()
                        answer_placeholder.empty()
                    except Exception as e:
                        error_info = f"Error occurred for user {user_id} question: {question}. Error: {str(e)}"
                        error_log.append(error_info)
                        st.error(error_info)

                    # Update progress bar and progress text
                    progress_bar.progress((i + 1) / question_count)
                    progress_text.text(f"Progress: User {user_id+1}/{user_count} - Question {i+1}/{question_count}")


            st.success(f"Volume testing completed with {user_count} users and {question_count} questions.")

        else:
            st.error("One or both of the uploaded files are not valid Excel files.")

    else:
        st.error("Please upload both user details and questions files.")

# Clean up the temporary directory when the app is closed or refreshed
try:
    temp_dir.cleanup()
except Exception as e:
    error_info = f"Error cleaning up temporary directory: {str(e)}"
    error_log.append(error_info)
    st.error(error_info)

# Store error_log for future evaluation
if error_log:
    # Store error_log in a file or database for future analysis
    # Example: error_log can be used to create a graph displaying information about the errors and their association with users and questions
    st.write("Errors occurred during volume testing. Please check the error log for details.")