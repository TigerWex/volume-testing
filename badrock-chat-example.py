from langchain.chains import LLMChain
from langchain_community.llms import Bedrock
from langchain.prompts import PromptTemplate
import boto3
import os
import streamlit as st

os.environ["AWS_PROFILE"] = "default"

# create bedrock client

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

modelID = "meta.llama3-8b-instruct-v1:0"
#modelID = "meta.llama3-70b-instruct-v1:0"

# Bedrock is from Langchain 
llm = Bedrock(
    model_id=modelID,
    client=bedrock_client,
    model_kwargs={"max_gen_len": 2000,"temperature":0.9}
)

# here we define function where we define the prompt and execute model
def my_chatbot(language,question):
    prompt = PromptTemplate(
        input_variables=["language", "question"],
        template="You are a chatbot. You are in {language}.\n\n{question}"
    )

    bedrock_chain = LLMChain(llm=llm, prompt=prompt)

    response=bedrock_chain({'language':language, 'question':question})
    return response

print(my_chatbot("english","who is buddha?"))

st.title("Bedrock Chatbot")

language = st.sidebar.selectbox("Language", ["english", "spanish"])

# if you select a language
if language:
    question = st.sidebar.text_area(label="what is your question?",
    max_chars=100)

# if we have a text in the text area control
if question:
    response = my_chatbot(language, question)
    st.write(response['text'])