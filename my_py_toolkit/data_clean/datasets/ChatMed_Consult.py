# from my_py_toolkit.file.toolkit import *
import sys
import json
from tqdm import tqdm
from os import remove

key_mapping = {
    "input": "question",
    "output": "response",
    "指示": "instruction",
    "指令": "instruction",
    "输入": "question",
    "输出": "response",
    "history": "chat",
    "query": "question"
}

def readjson(file_path):
  """"""
  with open(file_path, "r", encoding="utf-8") as f:
    return json.load(f)

def add_require_keys(value):
    keys = ['instruction', 'question', 'response']
    for k in keys:
        if k not in value:
            value[k] = ''
            # print(f'Miss key: {k}, {value}')
    return value

def check_values(value, keys):
    for k in keys:
        if k in value and not value[k] is None:
            return True
    return False

def check_keys_valid(value):
    keys = [['input', 'instruction', '指示', '指令', '输入', 'query'], ['output', '输出', 'response']]
    res = [check_values(value, k) for k in keys]
    if all(res):
        return True
    else:
        return False

def handle_chat(value):
    result = []
    for i, (question, response) in enumerate(value):
        result.append({
            'id': i,
            'question': question,
            'response': response
        })
    return result


def handle_value(value, key):
    if key == 'chat':
        value = handle_chat(value)
    
    return value


def handle_json_file(data_path, writer, writer_error):
    error_cts = 0
    for item in tqdm(readjson(data_path)):
        cur = {}
        if not check_keys_valid(item):
            print('=' * 80 + f'Invalid: \n ori: \n {item},\n')
            error_cts += 1
            writer_error.write(json.dumps(item, ensure_ascii=False) + '\n')
        else:

            for k,v in item.items():
                k = key_mapping.get(k, k)
                cur[k] = handle_value(v, k)
            
            cur = add_require_keys(cur)
            writer.write(json.dumps(cur, ensure_ascii=False) + '\n')
    return error_cts


def read_file(path, spl_char=None, ops=None, encoding='utf-8'):
    """
    读取文件内容, 并使用分隔符分割文本，对分割文本进行处理。

    Args:
        path (str): 文件路径
        spl_char (str, optional): 文件内容分隔符，eg: \n, 表示把文件内容按 \n 分成数组. Defaults to None.
        ops(function): 对值的处理函数
    """
    # TODO 后期把编码改 utf-8 试试
    with open(path, 'r', encoding=encoding) as f:
        data = f.read()
        if spl_char is not None:
            data = data.split(spl_char)
        if ops:
            data = ops(data)
        return data


def handle_jsonl_file(data_path, writer, writer_error):
    error_cts = 0
    for line in tqdm(read_file(data_path, '\n')):
        if not line:
            continue

        cur = {}
        item = json.loads(line)
        if not check_keys_valid(item):
            print('=' * 80 + f'Invalid: \n ori: \n {item},\n')
            error_cts += 1
            writer_error.write(json.dumps(item, ensure_ascii=False) + '\n')
        else:

            for k,v in item.items():
                k = key_mapping.get(k, k)
                cur[k] = handle_value(v, k)
            
            cur = add_require_keys(cur)
            writer.write(json.dumps(cur, ensure_ascii=False) + '\n')
    return error_cts

def main():
    data_path = sys.argv[1]
    save_path = data_path[:data_path.rfind('.')] + '_processed.jsonl'
    save_path_error = data_path[:data_path.rfind('.')] + '_error.jsonl'
    writer = open(save_path, 'w', encoding='utf-8')
    writer_error = open(save_path_error, 'w', encoding='utf-8')

    if len(sys.argv) < 3 or sys.argv[2] == 'json':
        error_cts = handle_json_file(data_path, writer, writer_error)
    elif len(sys.argv) > 2 and sys.argv[2] == 'jsonl':
        error_cts = handle_jsonl_file(data_path, writer, writer_error)
    
    if error_cts == 0:
        remove(save_path_error)
    

if __name__ == '__main__':
    main()




