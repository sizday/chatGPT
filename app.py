import os
import openai
from flask import Flask, redirect, render_template, request, url_for
from function.api import create_graph_by_text
from config import API_KEY

app = Flask(__name__)
openai.api_key = os.getenv(API_KEY)


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
        graph = create_graph_by_text(text=form_text,
                                     model_name=model_name)

        return render_template("index.html", result=graph.image, text=form_text)

    result = request.args.get("result")
    return render_template("index.html", result=result)


if __name__ == '__main__':
   app.run(debug=True)
