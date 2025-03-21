from flask import Flask, request, Response, session
import os
from openai import OpenAI
from dotenv import dotenv_values
from flask_session import Session
from redis import Redis

# Load .env configuration (adjust path as needed)
dotenv_path = r"c:\Users\Jakaria.Ahmed\OneDrive - insidemedia.net\Documents\cloud_backup\2025-Dev-Projects\Explore\nvidia-nim\.env"
env_config = dotenv_values(dotenv_path)
os.environ["env_openai_keys"] = env_config["OPENAI_KEY"]
# os.environ["env_openai_keys"] = env_config["OPENAI_KEY"]

app = Flask(__name__)
app.secret_key = "super_secret_key" 

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.environ["env_openai_keys"]
)

nutritionist_system_prompt = """
You are Dr. NutriGPT, a board-certified nutritionist with 15 years of clinical experience.
Combine evidence-based guidelines from:
1. WHO dietary recommendations (2025)

Always:
- Cite sources using [1][2] notation
- Provide meal plans with glycemic index considerations
Note:
- see prvious messages for context
- Use <br> for line breaks
-If returning any list, format the list using proper HTML structure like 
<b>Please share the following biometrics:</b>
<ul>
    <li><b>Age</b></li>
    <li><b>Sex</b></li>
    ...
 </ul>   
"""

# 🔥 FIX: Store sessions in the filesystem instead of cookies
app.config["SESSION_TYPE"] = "filesystem"  # Use local file storage
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_FILE_DIR"] = "./flask_session"  # Local storage directory

Session(app)  

@app.route("/query", methods=["POST"])
def query_model():
    user_input = request.json.get("input", "")

    # Ensure session messages exist
    if "messages" not in session:
        session["messages"] = []

    # Append user input to session messages
    session["messages"].append({"role": "user", "content": user_input})

    # Limit history (keep only the last 10 messages to prevent overflow)
    session["messages"] = session["messages"][-20:]
    session.modified = True  

    # Construct full message history for context retention
    messages = [{"role": "system", "content": nutritionist_system_prompt}] + session["messages"]

    # Debugging: Print messages before sending to model
    print("\n📌 Full Context Sent to Model:\n", messages, "\n")

    # Call OpenAI model with full context
    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=messages,
        temperature=0.2,
        top_p=0.7,
        max_tokens=2024,
        stream=True
    )

    def generate():
        full_response = ""
        try:
            for chunk in completion:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    text_piece = chunk.choices[0].delta.content
                    full_response += text_piece
                    yield f"data: {text_piece}\n\n"

            # Store assistant response in session
            session["messages"].append({"role": "assistant", "content": full_response})

            # Print updated session for debugging
            print("\n✅ Updated Session Messages:\n", session["messages"], "\n")

        except Exception as e:
            yield f"data: [Error] {str(e)}<br>\n\n"

    return Response(generate(), mimetype="text/event-stream")

# New route to check session data
@app.route("/session-data", methods=["GET"])
def get_session_data():
    return {"session": session.get("messages", [])}

# New route to reset session
@app.route("/reset-session", methods=["POST"])
def reset_session():
    session.pop("messages", None)
    return {"message": "Session reset."}

if __name__ == "__main__":
    app.run(debug=True)


