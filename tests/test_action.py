import pytest
from pathlib import Path
import os
import pandas as pd
import ast
import random
from typing import Optional, Any
from dotenv import load_dotenv
from config import API_KEY

import openai
from function.state import State
from function.graph import RelationsGraph
from function.rule_based import RuleBasedExtractor

MODEL_NAME = 'gpt-3.5-turbo'
# MODEL_NAME = 'text-davinci-003'
CSV_FILEPATH = 'data/mtsample/data.csv'
ENV_FILENAME = '.env'
PERCENT_RECALL = 0
PERCENT_PRECISION_RELATIONS = 0
PERCENT_PRECISION_ENTITY = 0
COUNT_DATA_TEST = 100
overall_recall = []
overall_precision_relations = []
overall_precision_entity = []


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
    print('Данные из csv файла загружены')
    df = pd.read_csv(data_csv_path, index_col=0)
    return df


@pytest.fixture()
def create_recall_precision_result():
    yield  # здесь происходит тестирование

    with open('C://Temp//Log.txt', 'a') as f:
        f.write(str(overall_recall) + '\n')
        f.write(str(overall_precision_relations) + '\n')
        f.write(str(overall_precision_entity) + '\n\n')


def non_empty_data_index() -> list:
    test_path = os.path.dirname(__file__)
    project_path = os.path.dirname(test_path)
    csv_path = os.path.join(project_path, CSV_FILEPATH)
    df = pd.read_csv(csv_path, index_col=0)
    df_non_empty_data = df.loc[df.Relations != '[]']
    non_empty_index_list = list(df_non_empty_data.index)
    count_data_test = min(COUNT_DATA_TEST, len(non_empty_index_list))
    non_empty_index_sublist = random.sample(non_empty_index_list, count_data_test)
    return non_empty_index_sublist


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
    tp, fn = _get_tp_and_fn(right_result, relations)
    recall = round(tp*100/tp+fn, 2)
    assert recall > PERCENT_RECALL, Alerts.result_should_be_right


@pytest.mark.test_case_id('T1.1')
@pytest.mark.test_case_name('Проверка усложненного примера')
def test_middle_case(setup_openai_key):
    text = "This 23-year-old white female presents with complaint of allergies. She used to have allergies when she " \
           "lived in Seattle but she thinks they are worse here. In the past, she has tried Claritin, and Zyrtec. " \
           "Both worked for short time but then seemed to lose effectiveness."
    right_result = [['person', 'sex', 'female'], ['person', 'age', '23'], ['person', 'race', 'white'],
                    ['person', 'has', 'allergies'], ['person', 'used', 'Claritin'], ['person', 'used', 'Zyrtec'],
                    ['person', 'lived', 'Seattle']]
    _test_by_gpt_and_right_result(right_result, text)


@pytest.mark.test_case_id('T1.2')
@pytest.mark.test_case_name('Проверка по всем непустым данным')
@pytest.mark.parametrize("index", non_empty_data_index())
def test_data_csv_case(setup_openai_key, df_from_csv, index):
    text = str(df_from_csv['Text data'][index])
    right_result_str: str = str(df_from_csv['Relations'][index])
    print(f"\n{str(df_from_csv['Medical Specialty'][index])}\n{str(df_from_csv['Sample Name'][index])}")
    right_result = ast.literal_eval(right_result_str)
    _test_by_gpt_and_right_result(right_result, text)


@pytest.mark.test_case_id('T2.1')
@pytest.mark.test_case_name('Проверка по всем непустым данным rule-based подходом')
@pytest.mark.parametrize("index", non_empty_data_index())
def test_data_csv_rule_based_case(setup_openai_key, df_from_csv, index):
    text = str(df_from_csv['Text data'][index])
    right_result_str: str = str(df_from_csv['Relations'][index])
    print(f"\n{str(df_from_csv['Medical Specialty'][index])}\n{str(df_from_csv['Sample Name'][index])}")
    right_result = ast.literal_eval(right_result_str)
    _test_by_rule_based_text_and_right_result(right_result, text)


def _test_by_rule_based_text_and_right_result(right_result, text):
    extractor = RuleBasedExtractor(text)
    relations = extractor.get_result()
    graph = RelationsGraph(relations)
    _check_text_and_right_result(graph, relations, right_result)


def _test_by_gpt_and_right_result(right_result, text):
    state = State()
    state.create_new_state(text=text, model_name=MODEL_NAME)
    graph = state.graph
    relations = graph.relations
    _check_text_and_right_result(graph, relations, right_result)


def _check_text_and_right_result(graph, relations, right_result):
    tp, fn = _get_tp_and_fn(right_result, relations)
    recall = round(tp * 100 / (tp + fn), 2)
    overall_recall.append(recall)
    print(f'Recall = {recall}%')
    assert isinstance(graph, RelationsGraph), Alerts.result_type_should_be_relation_graph
    assert recall > PERCENT_RECALL, Alerts.result_should_contain_right_dict
    new_relations = _get_new_relations(right_result, relations)
    new_entity = _get_new_entity(right_result, relations)
    relations_fp = len(new_relations)
    entity_fp = len(new_entity)
    relations_precision = round(tp * 100 / (tp + relations_fp), 2)
    entity_precision = round(tp * 100 / (tp + entity_fp), 2)
    overall_precision_relations.append(relations_precision)
    overall_precision_entity.append(entity_precision)
    print(f"\nPrecision relations = {relations_precision}\nPrecision entity = {entity_precision}")
    assert relations_precision > PERCENT_PRECISION_RELATIONS, Alerts.result_should_add_new_entity
    assert entity_precision > PERCENT_PRECISION_ENTITY, Alerts.result_should_add_new_entity


def _get_tp_and_fn(sublist, full_list):
    TP = 0
    FN = 0
    for sublist_elem in sublist:
        variants_sublist_elem = _create_variants_relation_list(sublist_elem)
        exist = False
        for variant in variants_sublist_elem:
            if variant in full_list:
                exist = True
                break
        if exist:
            TP += 1
        else:
            FN += 1

    return TP, FN


def _create_variants_relation_list(sublist_elem):
    first_entity, relation, second_entity = sublist_elem
    same_relation = _get_same_relation(relation)
    if same_relation:
        variants = [[first_entity, relation, second_entity],
                    [second_entity, relation, first_entity],
                    [first_entity, same_relation, second_entity],
                    [second_entity, same_relation, first_entity]]
    else:
        variants = [[first_entity, relation, second_entity],
                    [second_entity, relation, first_entity]]
    return variants


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


def _get_same_relation(relation: str) -> str:
    return {
        "had": "has",
        "has": "had",
        "is": "was",
        "was": "is",
        "live": "lives",
        "will live": "live",
        "lived": "live",
    }.get(relation)
