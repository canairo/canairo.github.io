#!/usr/bin/env python3
import subprocess
import os
from flask import Flask, request, render_template_string
from prots import *

app = Flask(__name__)

FORM = """
<!DOCTYPE html>
<html>
<body>
    <h2>Submit C code</h2>
    <form method="POST">
        <textarea name="code" cols="80" rows="20"></textarea><br>
        <button type="submit">Compile & Run</button>
    </form>

    {% if output %}
    <h3>Output</h3>
    <pre>{{ output }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return '<a href="/submit">Go to sandbox</a>'

@app.route("/submit", methods=["GET", "POST"])
def submit():
    output = None

    if request.method == "POST":
        code = request.form.get("code", "")

        code_path = "/sandbox/code.c"
        bin_path = "/sandbox/a.out"

        # check sandbox
        if not regex_protection(code):
            return render_template_string(FORM, output="failed the regex check")
        # Write C code
        with open(code_path, "w") as f:
            f.write(code)

        # Compile
        compile_cmd = ["gcc", code_path, "-o", bin_path]

        try:
            comp = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            output = "Compiler timed out"
            return render_template_string(FORM, output=output)

        if comp.returncode != 0:
            output = "Compilation failed:\n" + comp.stderr
            return render_template_string(FORM, output=output)

        # Run with limits (insecure on purpose)
        try:
            run = subprocess.run(
                [bin_path],
                capture_output=True,
                text=True,
                timeout=3,
                cwd="/sandbox"
            )
            output = run.stdout + run.stderr
        except subprocess.TimeoutExpired:
            output = "Execution timed out"

    return render_template_string(FORM, output=output)
    

if __name__ == "__main__":
    # Debug server, intentionally open for pentesting demo
    app.run(host="0.0.0.0", port=5000)

