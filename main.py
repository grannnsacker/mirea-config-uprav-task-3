import json
import sys
from sly import Lexer, Parser
from typing import Union
DATA = []


class ConfigLexer(Lexer):
    tokens = {NUMBER, STRING, LPAREN, RPAREN, NAME}
    ignore = ' \t'

    NUMBER = r'\d+'
    STRING = r'\".*?\"'
    NAME = r'\".*?\"'
    LPAREN = r'\('
    RPAREN = r'\)'

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')


class ConfigParser(Parser):
    tokens = ConfigLexer.tokens

    @_('LPAREN s_exp_list RPAREN')
    def s_exp(self, p):
        return p.s_exp_list

    @_('data')
    def s_exp(self, p):
        return p.data

    @_('s_exp s_exp_list')
    def s_exp_list(self, p):
        return [p.s_exp] + p.s_exp_list

    @_('s_exp')
    def s_exp_list(self, p):
        return [p.s_exp]

    @_('NAME', 'NUMBER', 'STRING')
    def data(self, p):
        return p[0]


def convert_to_json(data) -> Union[list, int, dict]:
    if type(data) is list:
        is_valid = True
        for item in data:
            if not (type(item) is list and len(item) == 2):
                is_valid = False
                break
        if is_valid:
            result = {}
            for item in data:
                key = item[0].replace('"', '')
                value = item[1]
                if not item[1].isdigit():
                    value = value.replace('"', '')
                if key == 'group' and value not in DATA:
                    DATA.append(value)
                result[key] = value
            return result
        else:
            new_data = []
            for item in data:
                if item:
                    new_item = convert_to_json(item)
                    new_data.append(new_item)
            return new_data
    elif type(data) is str and data.isdigit():
        return int(data)
    elif type(data) is dict:
        new_data = {}
        for key, value in data.items():
            new_data[key] = convert_to_json(value)
        return new_data
    else:
        return data.replace('"', '')


def to_json(data) -> list:
    result = convert_to_json(data)
    result.append(DATA)
    return result


def parse(subjects: list) -> dict:
    array = []
    for subject in subjects:
        json_result = to_json(ConfigParser().parse(ConfigLexer().tokenize(subject)))
        dict = {
            "subject": json_result[0],
            "students": json_result[1:-1],
            "groups": json_result[-1]
        }
        array.append(dict)

    return {"subjects": array}


def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    filename = sys.argv[1]
    text_array = []
    with open(filename, 'r', encoding='utf-8') as f:
        text = ""
        for line in f.readlines():
            text += line
            if line == ')\n':
                text_array.append(text)
                text = ""

    result = parse(text_array)
    answer = json.dumps(result, indent=2, ensure_ascii=False)
    with open('result.json', 'w', encoding='utf-8') as f:
        f.write(answer)
    print(answer)


if __name__ == '__main__':
    main()
