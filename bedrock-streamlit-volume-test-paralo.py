import os
import tempfile
import pandas as pd
import random
import boto3
from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import time
import certifi
import matplotlib.pyplot as plt
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Set the AWS profile and certificate bundle
os.environ["AWS_PROFILE"] = "default"
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Create a temporary directory for storing the uploaded files
temp_dir = tempfile.TemporaryDirectory()

# Set the model ID
model_id = "meta.llama3-8b-instruct-v1:0"

def validate_file(file):
    """
    Validates the uploaded file to ensure it can be read as an Excel file.
    
    Parameters:
    - file: file object uploaded by the user
    
    Returns:
    - Tuple (bool, int): True if the file is valid, and the number of rows in the file
    """
    try:
        df = pd.read_excel(file)
        return True, df.shape[0]
    except Exception as e:
        return False, 0

def initialize_bedrock_client():
    """
    Initializes the Bedrock client.
    
    Returns:
    - bedrock_client: boto3 client, initialized Bedrock client
    """
    return boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

def chat(question):
    """
    Sends a question to the Bedrock LLM and returns the response.
    
    Parameters:
    - question: str, the question to be sent
    
    Returns:
    - response: dict, the response from the LLM
    """
    prompt = PromptTemplate(
        input_variables=["question"],
        template="{question}"
    )

    bedrock_chain = LLMChain(llm=llm, prompt=prompt)
    response = bedrock_chain({'question': question})
    return response

def simulate_user_questions(user_id, questions, user_progress, user_time, response_times, avg_response_times, error_log, lock):
    """
    Simulates a user asking questions and updates the progress.
    
    Parameters:
    - user_id: int, ID of the user
    - questions: list, list of questions to ask
    - user_progress: dict, dictionary to store user progress
    - user_time: dict, dictionary to store time taken by the user
    - response_times: list, list to store response times for each question
    - avg_response_times: list, list to store average response times for each question
    - error_log: list, list to store error messages
    - lock: threading.Lock, lock to synchronize access to shared resources
    """
    random.shuffle(questions)
    for question in questions:
        try:
            start_time = time.time()
            response = chat(question)
            answer = response["text"]
            end_time = time.time()
            time_taken = end_time - start_time
            user_time[user_id] += time_taken
            response_times.append(time_taken)
            avg_response_times.append(sum(response_times) / len(response_times))
            user_progress[user_id]["answered"] += 1
        except Exception as e:
            error_info = f"Error occurred for user {user_id} question: {question}. Error: {str(e)}"
            error_log.append(error_info)
            user_progress[user_id]["error"] += 1

def update_plot(user_progress, user_time, response_times, avg_response_times, error_log):
    """
    Updates the plot showing the progress of users and other metrics.
    
    Parameters:
    - user_progress: dict, dictionary containing progress of users
    - user_time: dict, dictionary containing time taken by users
    - response_times: list, list of response times
    - avg_response_times: list, list of average response times
    - error_log: list, list of error messages
    """
    progress_df = pd.DataFrame(user_progress).T
    fig, axes = plt.subplots(2, 1, figsize=(10, 15))

    # Plot progress of answered questions for each user
    progress_df.plot(kind='bar', stacked=True, color=['green', 'red'], ax=axes[0])
    axes[0].set_xlabel('User ID')
    axes[0].set_ylabel('Number of Questions')
    axes[0].set_title('Progress of Answered Questions for Each User')
    axes[0].yaxis.get_major_locator().set_params(integer=True)

    # Annotate the bars with the time taken
    for p in axes[0].patches:
        width, height = p.get_width(), p.get_height()
        if height > 0:
            x, y = p.get_xy()
            user_id = int(x + width / 2)
            if user_progress[user_id]["answered"] > 0:  # Annotate only once per user
                time_text = f"time: {user_time[user_id] / 60:.2f} min"
                axes[0].annotate(time_text, (x + width / 2, height), 
                                 ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')

    # Display number of errors, successful answers, and total time taken
    total_errors = sum(user['error'] for user in user_progress.values())
    total_successes = sum(user['answered'] for user in user_progress.values())
    total_time_taken = sum(user_time.values()) / 60  # in minutes
    textstr = f'Total Errors: {total_errors}\nTotal Successful Answers: {total_successes}\nTotal Time Taken: {total_time_taken:.2f} min'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axes[0].text(0.05, 0.95, textstr, transform=axes[0].transAxes, fontsize=12,
                 verticalalignment='top', bbox=props)

    # Plot response times and average response times
    axes[1].plot(response_times, label='Response Time', color='orange')
    if avg_response_times:
        axes[1].plot(avg_response_times, label='Average Response Time', linestyle='--', color='blue')
    axes[1].set_xlabel('Request Number')
    axes[1].set_ylabel('Response Time (s)')
    axes[1].set_title('Response Times')
    axes[1].legend()

    return fig

def analyze_results(user_count, question_count, total_successes, total_errors, total_time_taken, avg_response_times, response_times, error_log):
    """
    Analyzes the volume test results using the Bedrock LLM.
    
    Parameters:
    - user_count: int, number of users
    - question_count: int, number of questions
    - total_successes: int, total successful answers
    - total_errors: int, total errors
    - total_time_taken: float, total time taken for the volume test
    - avg_response_times: list, average response times for each request
    - response_times: list, response times for each request
    - error_log: list, list of error messages
    
    Returns:
    - analysis: str, analysis provided by the LLM
    """
    avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0

    results_summary = f"""
    Volume Testing Results Summary:
    - Number of users: {user_count}
    - Number of questions: {question_count}
    - Total Successful Answers: {total_successes}
    - Total Errors: {total_errors}
    - Total Time Taken: {total_time_taken:.2f} minutes
    - Average Response Time: {avg_response_time:.2f} seconds
    - Maximum Response Time: {max_response_time:.2f} seconds
    - Minimum Response Time: {min_response_time:.2f} seconds
    
    Error Log:
    {error_log}
    """
    
    question = f"""
    We are testing a Large Language Model (LLM). Please analyze the following volume test results and provide insights on what is good, what problems exist, and how to improve performance if there are any issues.
    
    {results_summary}
    """
    
    response = chat(question)
    return response['text']

# Streamlit UI
st.title("Volume Testing Simulator for LLMs")

# Sidebar for file uploads
st.sidebar.title("Upload Files")

# Initialize validity flags
is_users_valid = False
is_questions_valid = False

users_file = st.sidebar.file_uploader("Choose a file with user details", type=["xlsx", "xls"])
questions_file = st.sidebar.file_uploader("Choose a file with questions", type=["xlsx", "xls"])

if users_file is not None:
    is_users_valid, user_count = validate_file(users_file)
    if is_users_valid:
        st.sidebar.write(f"Number of records in the user details file: {user_count}")
    else:
        st.sidebar.error("The user details file is not a valid Excel file.")
else:
    user_count = 0

if questions_file is not None:
    is_questions_valid, question_count = validate_file(questions_file)
    if is_questions_valid:
        st.sidebar.write(f"Number of records in the questions file: {question_count}")
    else:
        st.sidebar.error("The questions file is not a valid Excel file.")
else:
    question_count = 0

# Run Volume Test button
run_button = st.sidebar.button("Run Volume Test", disabled=(not is_users_valid or not is_questions_valid))

if run_button:
    if is_users_valid and is_questions_valid:
        users = pd.read_excel(users_file)
        questions_df = pd.read_excel(questions_file)

        if 'Question' not in questions_df.columns:
            st.error("Error: The 'Question' column is not found in the questions file.")
            st.write(f"Available columns are: {questions_df.columns.tolist()}")
        else:
            questions = questions_df["Question"].tolist()

            user_progress = {user_id: {"answered": 0, "error": 0} for user_id in users.index}
            user_time = {user_id: 0 for user_id in users.index}
            response_times = []
            avg_response_times = []
            error_log = []
            lock = Lock()

            bedrock_client = initialize_bedrock_client()

            llm = BedrockLLM(
                model_id=model_id,
                client=bedrock_client,
                model_kwargs={"max_gen_len": 512, "temperature": 0.5}
            )

            plot_placeholder = st.empty()

            with ThreadPoolExecutor(max_workers=user_count) as executor:
                futures = []
                for user_id in users.index:
                    futures.append(executor.submit(simulate_user_questions, user_id, questions, user_progress, user_time, response_times, avg_response_times, error_log, lock))
                    time.sleep(5)

                for future in as_completed(futures):
                    future.result()

            st.success(f"Volume testing completed with {user_count} users and {question_count} questions.")
            if error_log:
                st.error("Errors occurred during volume testing. Here are the details:")
                for error in error_log:
                    st.write(error)

            # Update the plot after all threads are done
            fig = update_plot(user_progress, user_time, response_times, avg_response_times, error_log)
            plot_placeholder.pyplot(fig)

            # Analyze the results using the LLM
            total_successes = sum(user['answered'] for user in user_progress.values())
            total_errors = sum(user['error'] for user in user_progress.values())
            total_time_taken = sum(user_time.values()) / 60  # in minutes
            analysis = analyze_results(user_count, question_count, total_successes, total_errors, total_time_taken, avg_response_times, response_times, error_log)
            st.subheader("LLM Analysis and Recommendations")
            st.write(analysis)
    else:
        st.error("Please upload both user details and questions files.")



