import requests
import time
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

# Retrieve sensitive data from environment variables
TOKEN_URL = os.getenv('TOKEN_URL')
KVANT_URL = os.getenv('KVANT_URL')
USERNAME = os.getenv('USERNAME')
API_KEY = os.getenv('API_KEY')
MODEL_ID = "meta-llama/llama-3-70b-instruct"
PROJECT_ID = os.getenv('PROJECT_ID')

# Placeholder variables to store token and its expiration time
ACCESS_TOKEN = None
TOKEN_EXPIRATION = 0  # Initialize as expired to trigger refresh on the first request

# Class for Claim Input
class ClaimInput(BaseModel):
    description: str

# Function to retrieve the Kvant access token
def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRATION

    if ACCESS_TOKEN is None or TOKEN_EXPIRATION < time.time():
        print("Token expired or not available. Requesting new token.")
        headers = {'Content-Type': 'application/json'}
        data = {
            "username": USERNAME,
            "api_key": API_KEY
        }

        response = requests.post(TOKEN_URL, headers=headers, json=data)
        if response.status_code == 200:
            token_data = response.json()
            ACCESS_TOKEN = token_data.get("token")
            expires_in = token_data.get("expires_in", 3600)
            TOKEN_EXPIRATION = time.time() + expires_in
            print(f"New token retrieved, expires in {expires_in} seconds.")
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve access token.")
    else:
        print("Using existing valid token.")
    
    return ACCESS_TOKEN

# Function to call the LLM endpoint for all tasks
def call_llm_endpoint(prompt_text):
    token = get_access_token()
    body = {
        "input": prompt_text,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        },
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(KVANT_URL, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Non-200 response: {response.text}")
    return response.json()['results'][0]['generated_text']

# Function to generate the NER prompt with examples
def getPromptNER(text):
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You always answer the questions with markdown formatting using GitHub syntax. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.

Any HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.

When returning code blocks, specify language.

You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Extract the following entities: Car model, Date, Time, and Location from the report below.

Input:
    The insured vehicle, a Tesla Model S, was parked outside on April 15th, 2023 when an unexpected and violent hailstorm struck the area. The hailstones caused extensive damage to the vehicle.
Named Entities:
    Car= Tesla Model S; Date= April 15th, 2023
Input:
    The insured vehicle, a Chevrolet Silverado, was involved in a hit and run accident on September 10th, 2023 at 3:30 PM on Oak Street.
Named Entities:
    Car= Chevrolet Silverado; Date= September 10th, 2023; Time= 3:30 PM; Location= Oak Street
Input:
    {text}
Named Entities:
"""

# Function to generate the summarization prompt
def getPromptSummary(description):
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You always answer the questions with markdown formatting using GitHub syntax. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.

Any HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.

When returning code blocks, specify language.

You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Please summarize the following insurance report in one paragraph.

Report: {description}

Summary:
"""

# Function to generate the next actions prompt with examples
def getPromptNextActions(summary):
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You always answer the questions with markdown formatting using GitHub syntax. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.

Any HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.

When returning code blocks, specify language.

You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Based on the summary below, suggest the next actions for this insurance claim.

Input:
    A car accident occurred on Jan 1st, 2023 at 5pm at the intersection of Woodbridge. The insured vehicle, a Honda Civic, was hit by another vehicle that ran a red light.
Output:
    1. Make a claim with your insurance company.
    2. Provide any paperwork required to substantiate the claim.
    3. Contact the insurance company and the covered driver.
Input:
    The insured vehicle, a Ford RAM, was stolen from Boston on Dec 2nd, 2022. The insured immediately reported the theft to the police and obtained a police report.
Output:
    1. Contact the police to file a police report.
    2. Provide the insurance company with the police report.
    3. Wait for the insurance company to contact you.
Input:
    {summary}
Output:
"""

# Extract named entities from the NER result
def getNER_FM(ner_str):
    car = ''
    loc = ''
    date = ''
    time = ''
    if len(ner_str) > 0:
        ner_arr = ner_str.split(';')
        for ner in ner_arr:
            if '=' in ner:
                entity_arr = ner.split('=')
                if entity_arr[0].strip() == 'Car':
                    car = entity_arr[1].strip()
                if entity_arr[0].strip() == 'Location':
                    loc = entity_arr[1].strip()
                if entity_arr[0].strip() == 'Date':
                    date = entity_arr[1].strip()
                if entity_arr[0].strip() == 'Time':
                    time = entity_arr[1].strip()
    return car, loc, date, time

# FastAPI route to process the insurance report
@app.post("/process_claim")
async def process_claim(claim: ClaimInput, request: Request):
    description = claim.description

    # Call NER task
    prompt_input_ner = getPromptNER(description)
    ner_str = call_llm_endpoint(prompt_input_ner)
    car, loc, date, time = getNER_FM(ner_str)

    # Call summarization task
    prompt_input_summary = getPromptSummary(description)
    summary = call_llm_endpoint(prompt_input_summary)
    summary = summary.replace('**','')

    # Call next actions task
    prompt_input_next_actions = getPromptNextActions(summary)
    next_actions = call_llm_endpoint(prompt_input_next_actions)
    next_actions = next_actions.replace('**','')

    return {
        "Car Model": car,
        "Location": loc,
        "Date": date,
        "Time": time,
        "Summary": summary,
        "Next Actions": next_actions
    }

# Main block to run the FastAPI app using uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
