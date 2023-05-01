import pytest
from pathlib import Path
import os
import pandas as pd
import ast
from typing import Optional, Any
from dotenv import load_dotenv
from config import API_KEY

import openai
from function.state import State
from function.graph import RelationsGraph

MODEL_NAME = 'gpt-3.5-turbo'
CSV_FILEPATH = 'data/mtsample/data.csv'
ENV_FILENAME = '.env'
PERCENT_TRUE = 90


class Alerts:
    result_should_be_right = "Результат должен быть равен правильному словарю"
    result_should_contain_right_dict = "Результат должен содержать правильный словарь"
    result_type_should_be_relation_graph = "Тип данных должен быть RelationGraph"
    result_accuracy_should_be_high = "Процент точности результата должен быть надежным"
    result_should_add_new_entity = "Результат должен добавлять новые сущности"


@pytest.fixture(scope='session')
def data_path() -> Path:
    return Path(__file__).parent.parent / 'data'


@pytest.fixture(scope='session')
def project_path() -> str:
    test_path = os.path.dirname(__file__)
    project_path = os.path.dirname(test_path)
    return project_path


@pytest.fixture(scope='session')
def load_env_file(project_path):
    dotenv_path = os.path.join(project_path, ENV_FILENAME)
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)


@pytest.fixture(scope='session')
def setup_openai_key(load_env_file):
    openai.api_key = os.getenv(API_KEY)
    if openai.api_key:
        print('\nOpenAI API Key is setup')
    else:
        raise Exception("\nНе удалось получить API key из .env\n")


@pytest.fixture(scope='session')
def data_csv_path(project_path) -> str:
    csv_path = os.path.join(project_path, CSV_FILEPATH)
    return csv_path


@pytest.fixture(scope='session')
def df_from_csv(data_csv_path):
    df = pd.read_csv(data_csv_path, index_col=0)
    return df


def non_empty_data_index() -> list:
    test_path = os.path.dirname(__file__)
    project_path = os.path.dirname(test_path)
    csv_path = os.path.join(project_path, CSV_FILEPATH)
    df = pd.read_csv(csv_path, index_col=0)
    df_non_empty_data = df.loc[df.Relations != '[]']
    return list(df_non_empty_data.index)


@pytest.mark.test_case_id('T1.0')
@pytest.mark.test_case_name('Проверка элементарного примера')
def test_clear_case(setup_openai_key):
    text = "Alice is Bob's roommate."
    right_result = [["Alice", "roommate", "Bob"]]
    state = State()
    state.create_new_state(text=text, model_name=MODEL_NAME)
    graph = state.graph
    relations = graph.relations
    assert isinstance(graph, RelationsGraph), Alerts.result_type_should_be_relation_graph
    assert _is_sublist(right_result, relations) > PERCENT_TRUE, Alerts.result_should_be_right


@pytest.mark.test_case_id('T1.1')
@pytest.mark.test_case_name('Проверка усложненного примера')
def test_middle_case(setup_openai_key):
    text = "This 23-year-old white female presents with complaint of allergies. She used to have allergies when she " \
           "lived in Seattle but she thinks they are worse here. In the past, she has tried Claritin, and Zyrtec. " \
           "Both worked for short time but then seemed to lose effectiveness."
    right_result = [['person', 'sex', 'female'], ['person', 'age', '23'], ['person', 'race', 'white'],
                    ['person', 'has', 'allergies'], ['person', 'used', 'Claritin'], ['person', 'used', 'Zyrtec'],
                    ['person', 'lived', 'Seattle']]
    _test_by_text_and_right_result(right_result, text)


@pytest.mark.test_case_id('T1.2')
@pytest.mark.test_case_name('Проверка по всем непустым данным')
@pytest.mark.parametrize("index", non_empty_data_index())
def test_data_csv_case(setup_openai_key, df_from_csv, index):
    text = str(df_from_csv['Text data'][index])
    right_result_str: str = str(df_from_csv['Relations'][index])
    print(f"{str(df_from_csv['Medical Specialty'][index])} {str(df_from_csv['Sample Name'][index])}")
    right_result = ast.literal_eval(right_result_str)
    _test_by_text_and_right_result(right_result, text)


def _test_by_text_and_right_result(right_result, text):
    state = State()
    state.create_new_state(text=text, model_name=MODEL_NAME)
    graph = state.graph
    relations = graph.relations
    assert isinstance(graph, RelationsGraph), Alerts.result_type_should_be_relation_graph
    assert _is_sublist(right_result, relations) > PERCENT_TRUE, Alerts.result_should_contain_right_dict

    new_relations = _get_new_relations(right_result, relations)
    new_entity = _get_new_entity(right_result, relations)
    print(f"\nNew entity = {new_entity}\nNew relations = {new_relations}")
    assert len(new_entity) > 0, Alerts.result_should_add_new_entity
    assert len(new_relations) > 0, Alerts.result_should_add_new_entity


def _is_sublist(sublist, full_list):
    count_true = 0
    count_false = 0
    for sublist_elem in sublist:
        if sublist_elem not in full_list:
            count_false += 1
        else:
            count_true += 1
    percent_true = int(count_true*100//(count_true+count_false))
    return percent_true


def _get_new_relations(right_result, result):
    new_relations = []
    for elem in result:
        if elem not in right_result:
            new_relations.append(elem)
    return new_relations


def _get_new_entity(right_result, result):
    right_entities = _get_all_entity(right_result)
    result_entities = _get_all_entity(result)
    new_entities = _get_difference_between_entities(right_entities, result_entities)
    return new_entities


def _get_all_entity(relations) -> list:
    nodes = []
    for first_entity, relation, second_entity in relations:
        nodes.append(first_entity)
        nodes.append(second_entity)
    nodes = list(set(nodes))
    return nodes


def _get_difference_between_entities(right_entities, result_entities):
    new_entities = []
    for result_entity in result_entities:
        if result_entity not in right_entities:
            new_entities.append(result_entity)
    return new_entities
