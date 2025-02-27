import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini AI Model
model = genai.GenerativeModel('gemini-1.5-flash')


def get_gemini_response(image_bytes, user_prompt):
    """
    Processes the medical image using Gemini AI and returns a diagnosis.
    """
    input_prompt = """
    You are a medical AI assistant specializing in analyzing medical images such as X-rays, MRIs, CT scans, and other diagnostic images.

    1️⃣ **Diagnosis:** Identify any medical condition or abnormality visible in the image.
    2️⃣ **Disease Name:** Provide the name of the detected disease (if applicable).
    3️⃣ **Symptoms:** List common symptoms associated with the detected condition.
    4️⃣ **Possible Causes:** Explain potential causes of the condition.
    5️⃣ **Treatment & Cure:** Suggest possible treatments, including medication, therapy, lifestyle changes, or surgical options if necessary.
    6️⃣ **Urgency:** Indicate whether the patient should seek immediate medical attention or consult a specialist.

    ⚠️ **Guidelines:**  
    - If the image is unclear, ask the user to upload a higher-quality scan.  
    - If the condition is not identifiable, advise the user to consult a medical professional.  
    - Be professional, concise, and medically accurate.  

    🔥 **Note:** You should ONLY provide medical insights. Do NOT generate random descriptions unrelated to medical analysis.
    """

    # Prepare image for AI model
    image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]

    # Get AI diagnosis
    response = model.generate_content([input_prompt, image_parts[0], user_prompt])

    return response.text