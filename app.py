import sys
import io
import threading
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Python Compiler</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 200px; font-family: 'Courier New', monospace; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; white-space: pre; overflow-x: auto; }
        button { padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #218838; }
        pre { background: #222; color: #00ff00; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; overflow-x: auto; white-space: pre-wrap; font-size: 14px; }
    </style>
    <script>
        window.addEventListener('DOMContentLoaded', () => {
            const textarea = document.getElementById('code-editor');
            
            textarea.addEventListener('keydown', function(e) {
                // 1. Handle Tab Key (inserts 4 spaces)
                if (e.key === 'Tab') {
                    e.preventDefault();
                    const start = this.selectionStart;
                    const end = this.selectionEnd;
                    this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
                    this.selectionStart = this.selectionEnd = start + 4;
                }
                
                // 2. Handle Enter Key (Auto-indent after colon)
                if (e.key === 'Enter') {
                    const start = this.selectionStart;
                    
                    // Get all text up to where the cursor currently is
                    const textUpToCursor = this.value.substring(0, start);
                    
                    // Isolate the current line being typed
                    const lines = textUpToCursor.split('\\n');
                    const currentLine = lines[lines.length - 1];
                    
                    // Check if the current line ends with a colon (ignoring trailing spaces)
                    if (currentLine.trim().endsWith(':')) {
                        e.preventDefault(); // Stop normal Enter key behavior
                        
                        // Calculate current indentation level of this line
                        const currentIndent = currentLine.match(/^\\s*/)[0];
                        // Add 4 more spaces to it
                        const nextIndent = currentIndent + "    ";
                        
                        const end = this.selectionEnd;
                        
                        // Insert the newline character followed by the calculated spacing
                        this.value = this.value.substring(0, start) + "\\n" + nextIndent + this.value.substring(end);
                        
                        // Reposition the blinking cursor right after the new indentation
                        this.selectionStart = this.selectionEnd = start + 1 + nextIndent.length;
                    }
                }
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <h2>Simple Python Online Compiler</h2>
        <p>Type your code below. Pressing <b>Enter</b> after a colon (<code>:</code>) will automatically indent 4 spaces!</p>
        
        <form method="POST">
            <textarea id="code-editor" name="code">{% if code is not none %}{{ code|safe }}{% else %}for i in range(1, 4):
    result = i * 5
    print(f"Loop {i}: {result}"){% endif %}</textarea>
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
        code = request.form.get("code", "").rstrip()
        
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        def run_user_code():
            try:
                exec(code, {"__builtins__": __builtins__}, {})
            except Exception as e:
                print(f"Execution Error:\n{str(e)}")

        thread = threading.Thread(target=run_user_code)
        thread.start()
        thread.join(timeout=2.0)

        if thread.is_alive():
            output = "Timeout Error: Code took longer than 2 seconds to execute!"
        else:
            output = redirected_output.getvalue()
            if not output:
                output = "[Code executed successfully with no print output]"
            
        sys.stdout = old_stdout
            
    return render_template_string(HTML_TEMPLATE, code=code, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
