from function.models import find_gpt_worker_by_format, ChatGPTModel
from function.graph import RelationsGraph
from typing import cast


class State:
    def __init__(self):
        self.graph = RelationsGraph([])

    def create_new_state(self, text, model_name):
        relations = self.__get_relations_by_text(model_name, text)
        self.graph = RelationsGraph(relations)

    def update_state(self, text, model_name):
        relations = self.__get_relations_by_text(model_name, text)
        self.graph.merge(relations)

    @staticmethod
    def __get_relations_by_text(model_name, text):
        GPTWorker = find_gpt_worker_by_format(model_name)
        gpt_worker = GPTWorker(text)
        gpt_worker = cast(ChatGPTModel, gpt_worker)
        gpt_worker.create_response()
        relations = gpt_worker.get_result()
        return relations
