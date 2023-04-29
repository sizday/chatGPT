import os
from typing import cast
import openai
from flask import Flask, redirect, render_template, request, url_for
from function.models import find_gpt_worker_by_format, ChatGPTModel
from function.graph import RelationsGraph

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        form_text = request.form["text"]
        if not form_text:
            result = request.args.get("result")
            return render_template("index.html", result=result)
        model_name = request.form["model"]
        if not model_name:
            result = request.args.get("result")
            return render_template("index.html", result=result)
        GPTWorker = find_gpt_worker_by_format(model_name)
        gpt_worker = GPTWorker(form_text)
        gpt_worker = cast(ChatGPTModel, gpt_worker)
        gpt_worker.create_response()
        result = gpt_worker.get_result()
        graph = RelationsGraph(result)

        return render_template("index.html", result=graph.image, text=form_text)

    result = request.args.get("result")
    return render_template("index.html", result=result)


if __name__ == '__main__':
   app.run(debug=True)
