import os
import subprocess
import sys

# AUTO-INSTALLER: This part handles the setup for you
def install_requirements():
    try:
        import flask
        import openai
    except ImportError:
        print("Installing missing tools... please wait.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "openai"])
        print("Installation complete! Restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)

install_requirements()

from flask import Flask, request, render_template_string
import io
import openai

app = Flask(__name__)

# CONFIGURATION
# Note: You need to set your OpenAI key in GitHub Secrets or the terminal
openai.api_key = os.getenv("OPENAI_API_KEY", "PASTE_KEY_HERE_IF_NOT_USING_ENV")

state = {
    "custom_logic": "# The AI will write code here.\nprint('System Ready. Awaiting Admin Command.')",
    "output": "System Initialized."
}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Admin Core</title>
    <style>
        body { font-family: monospace; background: #050505; color: #00ff00; padding: 30px; }
        .panel { border: 1px solid #00ff00; padding: 20px; box-shadow: 0 0 15px #00ff00; border-radius: 8px; }
        textarea { width: 100%; height: 300px; background: #000; color: #00ff00; border: 1px solid #00ff00; font-size: 16px; margin: 10px 0; }
        input { width: 80%; padding: 10px; background: #111; border: 1px solid #00ff00; color: #fff; }
        button { padding: 10px 20px; background: #00ff00; color: #000; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #fff; }
        .output-box { background: #111; padding: 15px; border-left: 3px solid #fff; margin-top: 20px; color: #00d9ff; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="panel">
        <h1>[ADMIN_CORE_v1.0]</h1>
        
        <form method="POST" action="/ai">
            <p>> COMMAND AI TO INNOVATE:</p>
            <input type="text" name="prompt" placeholder="e.g. Create a script to scan these files...">
            <button type="submit">AI GENERATE</button>
        </form>

        <form method="POST" action="/run">
            <textarea name="code">{{ code }}</textarea><br>
            <button type="submit" style="width:100%; height: 50px;">EXECUTE SYSTEM MODIFICATION</button>
        </form>

        <div class="output-box">
            <strong>LAST EXECUTION LOG:</strong>
            <pre>{{ output }}</pre>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML, code=state["custom_logic"], output=state["output"])

@app.route('/ai', methods=['POST'])
def ai_gen():
    prompt = request.form.get('prompt')
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an admin tool. Return ONLY executable Python code."},
                      {"role": "user", "content": prompt}]
        )
        state["custom_logic"] = response.choices[0].message.content
    except Exception as e:
        state["output"] = f"AI Error: {str(e)}"
    return render_template_string(HTML, code=state["custom_logic"], output=state["output"])

@app.route('/run', methods=['POST'])
def run_code():
    code = request.form.get('code')
    state["custom_logic"] = code
    f = io.StringIO()
    try:
        with io.StringIO() as buf, sys.stdout as old_stdout:
            sys.stdout = buf
            exec(code, globals())
            state["output"] = buf.getvalue()
    except Exception as e:
        state["output"] = f"Runtime Error: {str(e)}"
    finally:
        sys.stdout = sys.__stdout__
    return render_template_string(HTML, code=state["custom_logic"], output=state["output"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
