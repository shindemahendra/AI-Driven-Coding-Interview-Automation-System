from flask import Flask, send_from_directory, request, jsonify
from google import genai
from google.genai import types
import os
import pathlib
import time
from dotenv import load_dotenv

# This must be called at the very start to load the key before we need it.
# It reads the key "AIzaSyD6KSiIF8olwTTkvZHZFstUxXUbNRcYKUw" from ./.env
load_dotenv()

# --- Configuration & Path Setup ---
BASE_DIR = pathlib.Path(__file__).parent.resolve()
app = Flask(__name__,
            static_url_path='',
            static_folder=BASE_DIR)

# --- Gemini API Setup ---
client = None
# This will retrieve the key loaded by load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("=" * 60)
    print("FATAL ERROR: GEMINI_API_KEY is missing. Please check your .env file.")
    print("=" * 60)
else:
    print("SUCCESS: GEMINI_API_KEY detected via .env file.")
    try:
        # Initialize client using the API key read from the environment
        client = genai.Client(api_key=API_KEY)
        print("SUCCESS: Gemini Client initialized.")
    except Exception as e:
        print(f"FATAL ERROR: Gemini Client initialization failed. Error: {e}")


def extract_code_output(response) -> str:
    """
    CRITICAL FIX: Extracts the actual stdout/result from the structured
    code_execution_result part of the Gemini API response.
    """
    if response and response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            # Check if the part contains the CodeExecutionResult structure
            if part.code_execution_result and part.code_execution_result.output:
                return part.code_execution_result.output

    # Fallback to the general response text if the structured part is missing
    # (though typically empty for code execution tool use).
    return response.text if response.text else None


def execute_python_code_with_gemini(student_code: str) -> str:
    """Executes code using the Gemini Code Execution tool."""

    if client is None:
        return "Gemini API Execution Error: Client not initialized. API key is invalid or missing."

    config = types.GenerateContentConfig(
        tools=[
            types.Tool(
                code_execution=types.ToolCodeExecution()
            )
        ]
    )

    prompt = f"""
    Execute the following Python code using the code execution tool. 
    Return ONLY the output (stdout or stderr) of the execution. Do not provide any analysis, commentary, or extra text.

    CODE TO EXECUTE:
    {student_code}
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            # Use the new extraction function instead of response.text
            result_text = extract_code_output(response)

            if result_text is not None:
                return result_text.strip()

            # --- DEBUG LOGGING ---
            print(f"\n--- DEBUG LOG: Attempt {attempt + 1} Failed Response ---")
            print("Response text was None. Full response object (for error inspection):")
            print(response)
            print("----------------------------------------------------------\n")

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                # Check for safety filter block explicitly
                if response.candidates and response.candidates[0].finish_reason.name == 'SAFETY':
                    return "Gemini API Execution Error: Code execution request was blocked by safety filters."
                return "Gemini API Execution Error: Model returned an empty or invalid response after multiple retries."

        except Exception as e:
            print(f"DEBUG: Attempt {attempt + 1}: API Call failed with error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                return f"Gemini API Execution Error: API Call failed after multiple retries. Last error: {e}"


# --- Code Execution Endpoint ---
@app.route('/execute_code', methods=['POST'])
def handle_code_execution():
    try:
        data = request.get_json()
        source_code = data.get('source_code')
        language = data.get('language')

        if language != 'python':
            return jsonify({"error": "Only Python execution is supported by the Gemini API integration."}), 400

        result_text = execute_python_code_with_gemini(source_code)

        response_data = {
            "stdout": result_text,
            "stderr": "",
            "status": {"id": 3, "description": "Accepted"},
            "time": 0,
            "memory": 0
        }

        # Check if the result indicates an error (either API or code execution)
        if "Gemini API Execution Error:" in result_text:
            response_data['stderr'] = result_text
            response_data['stdout'] = ""
            response_data['status'] = {"id": 11, "description": "Execution Error"}
        # Check if the result is empty or just whitespace (meaning the code itself failed or produced no output)
        elif not result_text.strip():
            response_data['stderr'] = "Your code produced no output."
            response_data['stdout'] = ""
            response_data['status'] = {"id": 11, "description": "Execution Error"}

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}", "status_code": 500}), 500


# --- Root Route Fix: Serves gindex.html (Corrected) ---
@app.route('/')
def serve_index():
    # Corrected to match your file name: gindex.html
    return send_from_directory(app.static_folder, 'gindex.html')


# --- Static File Route (Serves script.js, problems.js, etc.) ---
@app.route('/<path:path>')
def serve_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    print(f"Flask serving static files from: {BASE_DIR}")
    app.run(host='0.0.0.0', port=5000)