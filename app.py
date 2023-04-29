import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        form_text = request.form["text"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(form_text),
            temperature=0.6,
        )
        result = response.choices[0].text.strip('.').strip().strip('\n')
        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(text):
    return """Given the current state of a graph and a prompt, extrapolate as many relationships as possible from the prompt and update the state. Every node has an id, label, and color (in hex). Every edge has a to and from with node ids, and a label. Edges are directed, so the order of the from and to is important.

Examples:
current state:
{ "nodes": [ { "id": 1, "label": "Bob", "color": "#ffffff" } ], "edges": [] }

prompt: Alice is Bob's roommate. Make her node green.

new state:
{ "nodes": [ { "id": 1, "label": "Bob", "color": "#ffffff" }, { "id": 2, "label": "Alice", "color": "#ff7675" } ], "edges": [ { "from": 1, "to": 2, "label": "roommate" } ] }

current state:
%s

prompt: %s

new state: """ % ('{ "nodes": [], "edges": [] }', text)
