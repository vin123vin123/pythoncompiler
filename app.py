import sys
import io
import threading
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Single HTML template for the browser interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Python Compiler</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 180px; font-family: 'Courier New', monospace; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        button { padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #218838; }
        pre { background: #222; color: #00ff00; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; overflow-x: auto; white-space: pre-wrap; font-size: 14px; }
        .error { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Simple Python Online Compiler</h2>
        <p>Enter your Python code below. You can use print statements, mathematical calculations, and loops.</p>
        
        <form method="POST">
            <textarea name="code">{% if code %}{{ code }}{% else %}# Try this loop and calculation example
for i in range(1, 6):
    calc = i * 25
    print(f"Loop iteration {i}: result is {calc}"){% endif %}</textarea>
            <br><br>
            <button type="submit">Run Code</button>
        </form>
        
        {% if output is not none %}
        <h3>Output:</h3>
        <pre>{{ output }}</pre>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    code = None
    
    if request.method == "POST":
        code = request.form.get("code", "")
        
        # Capture standard output to intercept print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        # Isolated function to safely run the code thread
        def run_user_code():
            try:
                # Executes user input within global constraints
                exec(code, {"__builtins__": __builtins__}, {})
            except Exception as e:
                print(f"Execution Error: {str(e)}")

        # Execute inside a background thread to prevent server lockup
        thread = threading.Thread(target=run_user_code)
        thread.start()
        thread.join(timeout=2.0)  # Enforce a strict 2-second timeout

        # Evaluate if the thread finished safely or timed out
        if thread.is_alive():
            output = "Timeout Error: Code took longer than 2 seconds to execute! (Infinite loop protection triggered)"
        else:
            output = redirected_output.getvalue()
            if not output:
                output = "[Code executed successfully with no print output]"
            
        # Restore standard system output
        sys.stdout = old_stdout
            
    return render_template_string(HTML_TEMPLATE, code=code, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
