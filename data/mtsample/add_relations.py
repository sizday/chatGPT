import pandas as pd
import ast

CSV_FILEPATH = 'data.csv'


def open_csv(filepath):
    df = pd.read_csv(filepath, index_col=0)
    return df


def save_csv(df, filepath):
    df.to_csv(filepath)


def find_data_by_sample_name(df, medical, sample_name):
    result = df.loc[(df['Sample Name'] == sample_name) & (df['Medical Specialty'] == medical)]
    if len(result) > 1:
        raise Exception("Неоднозначная запись")
    elif len(result) == 0:
        raise Exception("Не найдено записей")
    else:
        return result.index[0]


def chat_adding_relations():
    df = open_csv(CSV_FILEPATH)
    medical_speciality = input("Введи специальность врача: ")
    sample_name = input("Введи заголовок статьи: ")
    sample_index = find_data_by_sample_name(df, medical_speciality, sample_name)
    current_relations_str = df['Relations'][sample_index]
    current_relations = ast.literal_eval(current_relations_str)
    print(f"Текущие связи: {current_relations_str}")
    """print("Ввод новых связей в формате ENTITY1,RELATION,ENTITY2 (без пробелов)\n"
          "Когда захотите закончить и сохранить текущее состояние введите exit")"""
    while True:
        text_relation = input("Введи новую связь: ")
        if text_relation == "exit":
            print(f'Текущие связи для данной записи: {current_relations}')
            df['Relations'][sample_index] = current_relations
            save_csv(df, CSV_FILEPATH)
            return
        elif text_relation == 'clear':
            print(f'Все текущие связи для данной записи удалены')
            df['Relations'][sample_index] = []
            save_csv(df, CSV_FILEPATH)
            return
        elif text_relation == 'delete':
            text_relation = input(f'Введите запись на удаление: ')
            delete_relation_list = text_relation.split(',')
            delete_relation_list = [elem.strip().lower() for elem in delete_relation_list]
            try:
                current_relations.remove(delete_relation_list)
                print(f"Успешное удаление элемента {delete_relation_list}")
            except Exception:
                print(f"Ошибка удаление элемента {delete_relation_list}")
        else:
            new_relation_list = text_relation.split(',')
            new_relation_list = [elem.strip().lower() for elem in new_relation_list]
            if len(new_relation_list) != 3:
                print('Некорректная запись')
            elif new_relation_list in current_relations:
                print('Данная связь уже есть в списке')
            else:
                print(f'Добавлена запись {new_relation_list}')
                current_relations.append(new_relation_list)


def main():
    chat_adding_relations()


if __name__ == '__main__':
    main()
