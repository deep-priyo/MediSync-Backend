import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini AI Model
model = genai.GenerativeModel('gemini-1.5-flash')


def get_diagnosis(name, age, gender, symptoms, history):
    input_prompt = f"""
    You are an AI medical assistant. A patient has provided the following details:

    👤 **Patient Name:** {name}
    🎂 **Age:** {age}
    🚻 **Gender:** {gender}
    🔍 **Symptoms:** {symptoms}
    📜 **Past Medical History:** {history if history else "None"}

    Your task:
    1️⃣ **Diagnose** the possible disease(s) based on symptoms.
    2️⃣ **Explain Causes** of the disease.
    3️⃣ **Suggest Treatments** (medications, home remedies, and medical procedures).
    4️⃣ **Advise Next Steps**, such as consulting a doctor or lifestyle changes.
    5️⃣ **If the condition is critical, provide emergency alert and list top Indian hospitals.**

    ⚠️ **Important**: If symptoms indicate a life-threatening condition, warn the user and suggest immediate medical assistance.
    """

    # Get response from Gemini API
    response = model.generate_content(input_prompt).text

    # Regular Expression to Remove Any Disclaimer
    disclaimer_pattern = r"(?i)(?:\*\*Disclaimer:\*\*|I am an AI and .*? medical advice\.)"
    filtered_response = re.sub(disclaimer_pattern, "", response).strip()

    return filtered_response
