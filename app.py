import os
from typing import cast
import openai
from flask import Flask, redirect, render_template, request, url_for
from function.models import find_gpt_worker_by_format, ChatGPTModel

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

models = ['text-davinci-003', 'gpt-3.5-turbo']
model_name = models[0]


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        form_text = request.form["text"]
        GPTWorker = find_gpt_worker_by_format(model_name)
        gpt_worker = GPTWorker(form_text)
        gpt_worker = cast(ChatGPTModel, gpt_worker)
        gpt_worker.create_response()
        result = gpt_worker.get_result()

        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template("index.html", result=result)
