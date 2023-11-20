# from my_py_toolkit.file.file_toolkit import *
import sys
import json
from tqdm import tqdm
from os import remove
import traceback

def merge_dia(diags):
    result = []
    cur_role = ''
    cur_text = ''
    for role, text in diags:
        if role == cur_role:
            cur_text += text
        else:
            if text:
                result.append((cur_role, cur_text))
            cur_role = role
            cur_text = text
    if cur_text:
        result.append((cur_role, cur_text))
        
    result = [[role, text] for role,text in result if text]
    return result

def handle_dia(diag):
    result = []
    for item in diag:
        role = item['speaker']
        text = item['sentence']
        result.append((role, text))
    return result

def readjson(file_path):
  """"""
#   make_path_legal(file_path)
  with open(file_path, "r", encoding="utf-8") as f:
    return json.load(f)

def main():
    data_path = sys.argv[1]
    save_path = data_path[:data_path.rfind('.')] + '_handled.jsonl'
    save_error_path = data_path[:data_path.rfind('.')] + '_error.jsonl'
    data = readjson(data_path)
    writer = open(save_path, 'w', encoding='utf-8')
    writer_error = open(save_error_path, 'w', encoding='utf-8')
    error_cts = 0
    for id, content in tqdm(data.items()):
        try:
            diag = handle_dia(content['dialogue'])
            diag = merge_dia(diag)

            report = content['report']
            cur_res = {'id': id, 'dialogue':diag, 'medical_record': report}
            writer.write(json.dumps(cur_res, ensure_ascii=False) + '\n')
        except:
            error_cts += 1
            print(f'error_cts: {error_cts}, {traceback.format_exc()}')
            writer_error.write(json.dumps({id:content}, ensure_ascii=False) + '\n')
    print(f'error_cts: {error_cts}')
    if error_cts < 1:
        remove(save_error_path)



if __name__ == '__main__':
    main()