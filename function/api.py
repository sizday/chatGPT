from function.models import find_gpt_worker_by_format, ChatGPTModel
from function.graph import RelationsGraph
from typing import cast


def create_graph_by_text(text, model_name):
    GPTWorker = find_gpt_worker_by_format(model_name)
    gpt_worker = GPTWorker(text)
    gpt_worker = cast(ChatGPTModel, gpt_worker)
    gpt_worker.create_response()
    result = gpt_worker.get_result()
    graph = RelationsGraph(result)
    return graph
