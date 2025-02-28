import os
import prescription
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import TextModel  # AI model for text-based diagnosis
import ImageModel  # AI model for image-based diagnosis

app = Flask(__name__)

# Enable CORS properly for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all frontend requests


# Function to clean AI-generated text
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove bold markdown
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # Remove italic markdown
    return text.strip()


# 🔹 Image Analysis Route
@app.route("/analyze", methods=["POST"])
def analyze_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        uploaded_file = request.files["image"]
        image_bytes = uploaded_file.read()

        user_prompt = request.form.get("symptoms", "")
        if user_prompt == "":
            user_prompt = 'none'
        diagnosis = ImageModel.get_gemini_response(image_bytes, user_prompt)

        return jsonify({"diagnosis": diagnosis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Text-Based Diagnosis Route
@app.route('/diagnose', methods=['GET', 'OPTIONS'])
def get_report():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS Preflight Passed"}), 200

    name = request.args.get('name', '').strip()
    age = request.args.get('age', '').strip()
    gender = request.args.get('gender', '').strip()
    symptoms = request.args.get('symptoms', '').strip()
    medical_history = request.args.get('medicalHistory', '').strip()

    if not name or not age or not gender or not symptoms:
        return jsonify({"error": "Missing required parameters"}), 400

    raw_diagnosis = TextModel.get_diagnosis(name, age, gender, symptoms, medical_history)
    cleaned_diagnosis = clean_text(raw_diagnosis)

    return jsonify({
        "name": name,
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "medicalHistory": medical_history,
        "diagnosis": cleaned_diagnosis
    })


@app.route("/prescriptionanalyze", methods=["POST"])
def analyze_prescription():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No prescription image uploaded"}), 400

        uploaded_file = request.files["image"]

        # ✅ Save the uploaded file to a temporary directory
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)  # Ensure the directory exists
        image_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(image_path)  # Save file to disk

        # ✅ Process the image using the image path
        extracted_text = prescription.process_prescription(image_path)

        return jsonify({"extracted_text": extracted_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use Render's provided PORT
    app.run(host="0.0.0.0", port=port)
