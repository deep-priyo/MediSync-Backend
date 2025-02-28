import openai
import os
import base64
from PIL import Image
import io

# Print environment variables (for debugging)
print(os.environ)

# ✅ Hardcode the OpenAI API key
openai.api_key = "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"  # Replace with your actual key

# Debugging: Print to confirm key is set
print("OpenAI API Key:", openai.api_key)

# Check if the key is set correctly
if openai.api_key is None or openai.api_key.strip() == "":
    raise ValueError("OpenAI API key is missing!")

# Continue with your OpenAI API calls...


def encode_image(image):
    """Encodes image to Base64 format."""
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")  # Convert to PNG
    return base64.b64encode(image_bytes.getvalue()).decode("utf-8")


def process_prescription(image_path):
    """Processes a prescription image using GPT-4 Turbo Vision."""
    try:
        # Open image and encode
        image = Image.open(image_path).convert("RGB")
        image_base64 = encode_image(image)

        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-11-20",  # Use GPT-4 Turbo (supports vision)
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract and correct this prescription image for accuracy."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ],
                },
            ],
        )

        return response["choices"][0]["message"]["content"]

    except openai.error.OpenAIError as e:
        return f"Error processing prescription: {str(e)}"


# Example usage
if __name__ == "__main__":
    image_path = "./WhatsApp Image 2025-02-28 at 05.13.45.jpeg"  # Replace with actual image path
    result = process_prescription(image_path)
    print("Corrected Prescription:\n", result)
