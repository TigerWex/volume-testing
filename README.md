
1. Activate environment: .\.venv\Scripts\activate

2. run pip install -r requirements.txt

3. to avoid complaining about SSL certificate run the following command to install dependencies:
(.venv) PS C:\Users\W513032\source\repos\volume testing> pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

Here's the step-by-step description of the code and the improvements made:

The required packages and modules are imported.
The local_css function is defined to set the page to dark mode by reading and applying CSS from a file.
A temporary directory is created using tempfile.TemporaryDirectory() to store the uploaded files.
The validate_file function is defined to check if an uploaded file is a valid Excel file.
A client instance is created for Ollama using Client(host='http://localhost:11434').
The Streamlit sidebar is used to allow users to upload files with user details and questions.
The main content area is titled "Volume Testing Simulator" using st.title.
If both the users file and questions file are uploaded, the code proceeds to process them.
The uploaded files are saved to the temporary directory.
The validate_file function is used to check the validity of the uploaded files.
If the files are valid, the user details and questions are read using pandas.
A progress bar is created using st.progress to visualize the progress of the volume testing.
The simulate_user function is defined to simulate volume testing for each user.
Inside the simulate_user function, a random question is selected from the list of questions.
The chat method is used to interact with the Llama3 8B model, and the response is obtained.
The user ID, question, and LLaMA 8B answer are displayed using st.write.
Exception handling is added to catch any errors that occur during the interaction with the Llama3 model.
A small delay is added using time.sleep to simulate some delay between questions.
The progress bar is updated to reflect the progress of the volume testing.
The simulate_user function is executed concurrently using ThreadPoolExecutor.
After all users have completed their questions, a success message is displayed with the total user and question count.
If one or both of the uploaded files are not valid Excel files, an error message is displayed.
Error handling is added to clean up the temporary directory when the app is closed or refreshed.
CSS for dark mode is written to a file to style the Streamlit app.



## 💻 Local Lllama-3 with RAG
Streamlit app that allows you to chat with any webpage using local Llama-3 and Retrieval Augmented Generation (RAG). This app runs entirely on your computer, making it 100% free and without the need for an internet connection.


### Features
- Ask questions 
- Get accurate answers using RAG and the Llama-3 model running locally on your computer


4. Run the Streamlit App
```bash
streamlit run streamlit-volume-test.py

```

### How it Works?

- The app loads the webpage data using WebBaseLoader and splits it into chunks using RecursiveCharacterTextSplitter.
- It creates Ollama embeddings and a vector store using Chroma.
- The app sets up a RAG (Retrieval-Augmented Generation) chain, which retrieves relevant documents based on the user's question.
- The Llama-3 model is called to generate an answer using the retrieved context.
- The app displays the answer to the user's question.

