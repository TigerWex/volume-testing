import os
import tempfile
import pandas as pd
import streamlit as st
import random
import boto3
from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import time
import certifi
import matplotlib.pyplot as plt

# Set the AWS profile
os.environ["AWS_PROFILE"] = "default"
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

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

# Create the Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Set the model ID
model_id = "meta.llama3-8b-instruct-v1:0"

# Create the Bedrock instance
llm = BedrockLLM(
    model_id=model_id,
    client=bedrock_client,
    model_kwargs={"max_gen_len": 512, "temperature": 0.5}
)

# Define the chat function
def chat(question):
    prompt = PromptTemplate(
        input_variables=["question"],
        template="{question}"
    )

    bedrock_chain = LLMChain(llm=llm, prompt=prompt)

    response = bedrock_chain({'question': question})
    return response

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

# Create a placeholder for the plot
plot_placeholder = st.empty()

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

            user_progress = {}  # Dictionary to store the progress for each user
            user_time = {}  # Dictionary to store the total time taken for each user

            # Simulate volume testing
            for user_id in users.index:
                user_progress[user_id] = {"answered": 0, "error": 0}  # Initialize progress for each user
                user_time[user_id] = 0  # Initialize total time taken for each user
                random.shuffle(questions)  # Shuffle the questions for each user

                for i, question in enumerate(questions):
                    try:
                        # Create placeholders for the question and answer
                        question_placeholder = st.empty()
                        answer_text_area = st.empty()
                        # Display the question right away
                        question_placeholder.write(f"UserId {user_id}: {question}")

                        # Start the timer
                        start_time = time.time()

                        # Display a waiting indicator while waiting for the answer from the model
                        with st.spinner('Waiting for the answer...'):
                            response = chat(question)
                            answer = response["text"]
                            # Update the answer text area with the answer
                            answer_text_area.text_area("LLama3 8B Answer", value=answer, height=200)

                        # Stop the timer
                        end_time = time.time()
                        time_taken = end_time - start_time
                        user_time[user_id] += time_taken

                        # Introduce a delay before clearing the question and answer placeholders
                        time.sleep(2)  # Delay for 2 seconds
                        # Erase the question and answer
                        question_placeholder.empty()
                        answer_text_area.empty()
                        user_progress[user_id]["answered"] += 1  # Increment the total answered questions
                    except Exception as e:
                        error_info = f"Error occurred for user {user_id} question: {question}. Error: {str(e)}"
                        error_log.append(error_info)
                        st.error(error_info)
                        user_progress[user_id]["error"] += 1  # Increment the total error count

                    # Update progress bar and progress text
                    progress_bar.progress((i + 1) / question_count)
                    progress_text.text(f"Progress: User {user_id+1}/{user_count} - Question {i+1}/{question_count}")

                    # Create a DataFrame from the user_progress dictionary
                    progress_df = pd.DataFrame(user_progress).T

                    # Clear the previous plot
                    plot_placeholder.empty()

                    # Plot the progress for each user
                    fig, ax = plt.subplots(figsize=(10, 5))  # Set a reasonable size for the plot
                    progress_df.plot(kind='bar', stacked=True, color=['green', 'red'], ax=ax)
                    ax.set_xlabel('User ID')
                    ax.set_ylabel('Number of Questions')
                    ax.set_title('Progress of Answered Questions for Each User')
                    ax.yaxis.get_major_locator().set_params(integer=True)  # Ensure y-axis has integer values only

                    # Display time taken on each bar
                    for p in ax.patches:
                        user_id = int(p.get_x() + p.get_width() / 2)
                        time_text = f"time: {user_time[user_id] / 60:.2f} min"
                        ax.annotate(time_text, (p.get_x() + p.get_width() / 2, p.get_height() + 0.5), 
                                    ha='center', va='center', fontsize=10, color='black', fontweight='bold')

                    plot_placeholder.pyplot(fig)  # Display the plot below the text areas

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
