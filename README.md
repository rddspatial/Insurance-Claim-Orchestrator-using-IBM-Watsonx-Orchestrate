# Insurance-Claim-Orchestrator-using-IBM-Watsonx-Orchestrator-IBM-Watsonx.ai-and-On-Prem-Vela

This project demonstrates how to create an LLM pipeline calling IBM Watsonx.ai LLMs hosted on-prem and create a FastAPI server, which can be deployed as  abackend API (on IBM Code Engine or any container execution engine or a VM). Then an OpenAPI spec can be created which can be used to create the skill/skill flow in Watsonx Orchestrate to perform certains tasks, such as, in this case, processing claims and retrieving named entities, creating summary and recommedning next actions. 

# Overview of Watsonx Orchestrate, Watsonx.ai, and Vela: 

# Watsonx Orchestrate (WxO): 
An AI-powered orchestration platform that streamlines task automation by enabling business users to run workflows and manage processes through AI-driven skills. WxO enables users to interact through a chat interface or an AI studio (Watsonx Assistant interface) and automates decision-making, task handling, and communication workflows. 
To learn more about IBM Watsonx Orchestrate please follow https://www.youtube.com/watch?v=UKmMmbUK1Ng

# Watsonx.ai: 
A suite of large language models (LLMs) designed to process natural language and perform complex tasks such as summarization, named entity recognition (NER), and recommendation generation. Watsonx.ai models can be deployed on-premises or in the cloud, providing organizations with flexibility in deploying their AI workloads. 
To learn more about IBM Watsonx.ai please follow https://www.ibm.com/products/watsonx-ai?

# Vela: 
The on-prem version of Watsonx.ai, installed on Red Hat OpenShift, providing foundation models with capabilities for businesses needing data sovereignty and in-house AI solutions. 
How to Connect to on-prem Vela (Kvant platform) and get the credentials: 
https://documentation.kvant.cloud/products/kvantai/kvantaiaas/kvantaisandbox/apikey_and_tokens/ 


# Use Case Overview: 
The insurance industry faces the challenge of managing and processing large volumes of claims daily. In this use case, the insurance case officer receives numerous auto insurance claims, each requiring extraction of specific information, report summarization, and communication of next steps to the claimant. 

IBM Watsonx Orchestrate integrates with Watsonx.ai to automate these tasks using foundation models. The end-to-end workflow is executed with minimal human intervention, significantly reducing processing time and costs while improving claim accuracy. 

# Workflow Description: 

1. Claim Report Submission: Claim reports are submitted to the insurance company and stored in a central database. 

2. WxO Dashboard Interaction: The insurance case officer logs into the Watsonx Orchestrate dashboard and retrieves the list of new claims. From here, they initiate a skill flow by clicking on the "Process Insurance Claim" skill. 

3. Skill Flow Execution: 

  * 3.1. The "Process Insurance Claim" skill retrieves the claim report from the database. 

  * 3.2. It triggers a series of tasks including: 

  * 3.3. Named Entity Recognition (NER): Identifies key information such as the car model involved in the accident, accident date, time, and location. 

  * 3.4. Report Summarization: Condenses the claim report into a concise summary for easy understanding. 

  * 3.5. Action Recommendation: Suggests next steps for the claimant based on the details of the claim. 

4. Automated Communication: After processing the claim, a secondary skill "Send Email" is triggered, which composes an email to the claimant. The email includes a summary of the incident, recommended next steps, and any necessary documents. Finally, the system sends the email automatically. For this project, we used a Gmail skill integration. However other mailing services such as Outlook can also be integrated as required.

# Architecture diagram
<img width="1512" alt="Screenshot 2024-10-16 at 18 41 52" src="https://github.com/user-attachments/assets/99adb855-93af-48a0-83ad-341e526fc640">

# Technical Details: 

 * OpenAPI Specification: Each skill in Watsonx Orchestrate is created based on an OpenAPI spec that defines the structure of APIs. In this project, the OpenAPI spec outlined the endpoints and required inputs for processing insurance claims. 

 * API Communication via IBM Code Engine: Watsonx Orchestrate calls an API hosted on IBM Code Engine, where a FastAPI server handles the requests. The FastAPI server uses secure authentication to interact with Watsonx.ai endpoints, leveraging foundation models to complete tasks like NER, summarization, and recommendations. The input to the models is the insurance claim report, and each task is mapped to a specific model. 

 * LLM Integration and Response Handling: The FastAPI server routes the claim report to the appropriate Watsonx.ai LLM endpoint. The model processes the input and returns a JSON response containing the results. The results are then sent back to Watsonx Orchestrate, which collates the information and presents it to the insurance case officer or triggers the next task in the workflow. 

 * Scalability with IBM Code Engine: The solution is designed to scale based on the workload, with IBM Code Engine automatically adjusting the number of instances depending on the load. This ensures that the system remains efficient and responsive even as the number of claims processed increases. 

 * Cloud-Agnostic Architecture: Although the current implementation uses IBM Code Engine and FastAPI, the architecture is adaptable to other cloud providers: 

 * For AWS, the IBM Code Engine component could be replaced with AWS Fargate or AWS Lambda. For Azure, Azure Container Apps could serve as the alternative platform for hosting the FastAPI server. This flexibility allows organizations to choose the cloud provider that best suits their operational requirements. 


P.S: You need to set the credentials in .env file with the right URLS and credentials and also you need to set the right code engine URL/endpoint in the OpenAPI spec before you could run the code and create the skill for Watsonx Orchestrate. 




