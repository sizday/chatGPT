import pytest
from pathlib import Path
import os
from typing import Optional, Any
from dotenv import load_dotenv
from config import API_KEY

import openai
from function.api import create_graph_by_text
from function.graph import RelationsGraph

MODEL_NAME = 'gpt-3.5-turbo'


class Alerts:
    result_should_be_right = "Результат должен быть равен правильному словарю"
    result_type_should_be_relation_graph = "Тип данных должен быть RelationGraph"
    result_accuracy_should_be_high = "Процент точности результата должен быть надежным"


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent.parent / 'data'


@pytest.fixture()
def project_path() -> str:
    test_path = os.path.dirname(__file__)
    project_path = os.path.dirname(test_path)
    return project_path


@pytest.fixture()
def load_env_file(project_path):
    dotenv_path = os.path.join(project_path, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)


@pytest.fixture()
def setup_openai_key(load_env_file):
    openai.api_key = os.getenv(API_KEY)
    if openai.api_key:
        print('OpenAI API Key is setup')
    else:
        raise Exception("Не удалось получить API key из .env")


@pytest.mark.test_case_id('T1.0')
@pytest.mark.test_case_name('Проверка элементарного примера')
def test_clear_case(setup_openai_key):
    text = "Alice is Bob's roommate."
    right_result = [["Alice", "roommate", "Bob"]]
    graph = create_graph_by_text(text=text,
                                 model_name=MODEL_NAME)
    relations = graph.relations
    assert isinstance(graph, RelationsGraph), Alerts.result_type_should_be_relation_graph
    assert relations == right_result, Alerts.result_should_be_right
