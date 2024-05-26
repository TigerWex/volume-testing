
1. Activate environment: .\.venv\Scripts\activate

2. run pip install -r requirements.txt

3. to avoid complaining about SSL certificate run the following command to install dependencies:
(.venv) PS C:\Users\W513032\source\repos\volume testing> pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

Here's the step-by-step description of the code and the improvements made:

Volume Testing Simulator for Large Language Models
Overview
This repository contains a Python script designed to simulate a volume test for Large Language Models (LLMs). The purpose of this script is to evaluate the performance of an LLM by simulating multiple users asking a series of questions in parallel. The script collects various performance metrics such as response times, error rates, and total processing time, and visualizes these metrics in real-time.

Key Features
Parallel User Simulation: Simulates multiple users asking questions simultaneously, with a staggered start to emulate real-world usage.
Real-time Visualization: Provides real-time plots to monitor the progress and performance metrics during the test.
Performance Metrics: Collects and displays metrics such as response times, total errors, successful answers, and total processing time.
LLM Analysis: Uses the LLM itself to analyze the results and provide insights and recommendations for performance improvements.
Prerequisites
Before running the script, ensure you have the following installed:

Python 3.6 or higher
Required Python libraries (listed in requirements.txt):
pandas
boto3
certifi
matplotlib
concurrent.futures
IPython.display
threading
Usage
Prepare Input Files:

users.xlsx: An Excel file containing user details. Each row represents a user.
questions.xlsx: An Excel file containing a list of questions. Each row represents a question.
Configure AWS Credentials:

Ensure your AWS credentials are configured correctly, as the script uses AWS services.
Run the Script:

Execute the script to start the volume test. The script will:
Validate the input files.
Display the number of user records and questions.
Simulate users asking questions to the LLM.
Visualize the performance metrics in real-time.
Provide an analysis of the results using the LLM.

Script Description
Here’s a detailed breakdown of what the script does:

Environment Setup:

Sets AWS profile and certificate bundle.
Creates a temporary directory for file storage.
File Validation:

Validates the input Excel files (users.xlsx and questions.xlsx).
Displays the number of records in each file.
Initialize LLM Client:

Sets up the Bedrock LLM client using AWS services.
Simulate User Questions:

Simulates each user asking a series of questions.
Collects response times and tracks errors.
Updates real-time plots to visualize progress and performance.
Update Plots:

Plots the progress of answered questions for each user.
Displays total errors, successful answers, and total processing time.
Plots response times and average response times.
Analyze Results:

Summarizes the test results.
Uses the LLM to analyze the results and provide insights and recommendations.
Results and Analysis
After the test completes, the script provides a detailed summary of the performance metrics, including:

Number of users and questions.
Total successful answers and errors.
Total time taken for the test.
Average, maximum, and minimum response times.
Additionally, the LLM will analyze these results and provide feedback on what is good, what problems exist, and how to improve the performance.

Conclusion
This script is a powerful tool for evaluating the performance of Large Language Models under load. By simulating real-world usage and collecting comprehensive performance metrics, it helps in identifying strengths and areas for improvement in the model.

For any questions or issues, please feel free to open an issue in this repository.

