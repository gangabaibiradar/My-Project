Support Assistant – AI Agent

This project is developed as part of the 48-Hour AI Agent Development Challenge.
The Support Assistant is designed to help users by answering FAQs, resolving simple support queries, and identifying cases that require human intervention.

1. Overview

The Support Assistant is an AI-powered tool that responds to user queries based on a predefined knowledge base. It helps automate basic customer support tasks such as answering common questions, giving quick replies, and escalating complex issues to a human support team.

The agent uses an LLM model for natural language understanding and a small FAQ dataset as its knowledge source.

2. Features

FAQ-Based Responses: Answers common questions using internal FAQ data.

Complex Query Detection: Flags issues that require human support.

Clean Streamlit Interface: Simple and easy-to-use UI.

Instant Responses: Generates replies in real-time.

Extendable: FAQ data and model logic can be modified easily.

3. Tech Stack

Python

Streamlit – for the UI

OpenAI GPT API – for generating responses

Custom Rules – to detect complex queries

Text-based FAQ file – as the internal knowledge base

Setup and run
How to Run the Project (Local Setup)
Step 1 — Install Python

Make sure Python 3.10+ is installed.

Step 2 — Install requirements

Open terminal inside your project folder and run:

pip install -r requirements.txt

Step 3 — Add your OpenAI API Key

Create a .env file:

OPENAI_API_KEY=your_key_here

Step 4 — Run the Streamlit App
streamlit run app.py


The browser will open automatically at:

http://localhost:8501
