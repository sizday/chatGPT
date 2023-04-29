import openai

_file_worker = dict()


def find_gpt_worker_by_format(fmt_name: str) -> 'ChatGPTModel':
    reg = _file_worker
    cls = reg.get(fmt_name)
    if not cls:
        cls = reg['abstract']
    return cls


def register_gpt_worker(cls):
    if not issubclass(cls, ChatGPTModel):
        raise TypeError(f'Class {cls} is not a writer')
    fmt_name = cls.model_name
    reg = _file_worker
    if fmt_name in reg:
        raise KeyError(f'Writer for format {fmt_name} already registered')
    reg[fmt_name] = cls
    return cls


class ChatGPTModel:
    model_name = 'default'

    def __init__(self, input_text):
        self.input_text = input_text
        self.response = None

    def generate_message(self):
        pass

    def create_response(self):
        pass

    def get_result(self):
        pass


@register_gpt_worker
class CompetitionGPTModel(ChatGPTModel):
    model_name = 'text-davinci-003'

    def generate_message(self):
        prompt = _read_prompt()
        prompt = prompt + self.input_text + '\n' + 'updates:'
        return prompt

    def create_response(self):
        self.response = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.generate_message(),
            temperature=0.6,
            max_tokens=800
        )

    def get_result(self):
        result = self.response.choices[0].text.strip('.').strip().strip('\n')
        return result


@register_gpt_worker
class ChatCompetitionGPTModel(ChatGPTModel):
    model_name = 'gpt-3.5-turbo'

    def generate_message(self):
        prompt = _read_prompt()
        prompt = prompt + self.input_text + '\n' + 'updates:'
        messages = _create_chat_messages(prompt)
        return messages

    def create_response(self):
        self.response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.generate_message(),
            temperature=0.6,
            max_tokens=800
        )

    def get_result(self):
        result = self.response.choices[0].message.content.strip('.').strip().strip('\n')
        return result


def _read_prompt():
    with open('prompts/statefull.prompt', 'r') as f:
        prompt = f.read()

    return prompt


def _create_chat_messages(prompt):
    messages = [{'role': 'system', 'content': prompt}]
    return messages


