import os
import openai
from flask import Flask, redirect, render_template, request, url_for
from function.state import State
from config import API_KEY

app = Flask(__name__)
openai.api_key = os.getenv(API_KEY)
state = State()


@app.route("/", methods=["POST"])
def index_post():
    form_text = request.form["text"]
    model_name = request.form["model"]

    if form_text and model_name:
        if request.form['action'] == "Generate graph":
            state.create_new_state(text=form_text, model_name=model_name)
        elif request.form['action'] == "Add to current graph":
            state.update_state(text=form_text, model_name=model_name)

        return render_template("index.html", result=state.graph.image, text=form_text)

    result = request.args.get("result")
    return render_template("index.html", result=result)


@app.route("/", methods=["GET"])
def index_get():
    result = request.args.get("result")
    return render_template("index.html", result=result)


if __name__ == '__main__':
    app.run(debug=True)
