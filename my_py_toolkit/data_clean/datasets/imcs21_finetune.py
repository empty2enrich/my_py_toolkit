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


def get_all_history_prompt(history, max_len=4096):
    conv = ''
    if isinstance(history[0], str):
        for i, value in enumerate(history):
            role = '医生' if i % 2 == 0 else '患者'
            cur = f'{role}：{value}\n'
            if len(conv) + len(cur) > max_len:
                break
            else:
                conv += cur
    elif isinstance(history[0], (tuple, list)):
        for role, value in history:
            if isinstance(role, int):
                role = '医生' if role == 0 else '患者'
            cur = f'{role}：{value}\n'
            if len(conv) + len(cur) > max_len:
                break
            else:
                conv += cur
    elif isinstance(history[0], dict):
        last_role = ''
        for his in history:
            for role, text in his.items():
                if len(f'{role}：{text}\n') + len(conv) > max_len:
                    break
                if last_role != role:
                    conv += f'\n{role}：{text}' if conv else f'{role}：{text}'
                    last_role = role
                else:
                    conv += f'{text}；'


        conv += '\n'
    # print(f'history all prompt: {conv}')
    return conv

def handle_record(record):
    result = {}
    mapping = {
        '建议': '治疗建议',
        '诊断': '诊断',
        '检查': '检查检验结果',
        '辅助检查': '检查检验结果',
        '主诉': '主诉',
        '现病史': '现病史',
        '既往史': '既往史',
        '个人史': '个人史',
        '婚育史': '婚育史',
        '家族史': '家族史'
    }
    for k,v in record.items():
        ori_key = mapping.get(k, k)
        if ori_key not in result:
            result[ori_key] = ''
        result[ori_key] += v
    return result
    


instruction = '给定医生和患者的对话内容，请生成一份患者的病历信息报告，' \
           '包括{主诉，现病史, 既往史，过敏史，个人史，婚育史，家族史，检查检验结果, 治疗建议}。如果没有则写“无”,并用严格用json格式输出。' \
           "json格式为：{'主诉':''，'现病史':'', '既往史': ''，'过敏史':''，'个人史':''，'婚育史':''，'家族史':''，'检查检验结果':'', '治疗建议':''}。"\
            "医生患者对话内容：\n"



def main():
    data_paths = sys.argv[1:]
    for data_path in data_paths:
        save_path = data_path[:data_path.rfind('.')] + '_finetune.jsonl'
        save_error_path = data_path[:data_path.rfind('.')] + '_error.jsonl'
        writer = open(save_path, 'w', encoding='utf-8')
        # writer_error = open(save_error_path, 'w', encoding='utf-8')
        cts = 0
        with open(data_path, 'r', encoding='utf-8') as r:
            line = r.readline()
            while line:
                try:
                    cur_data = json.loads(line)
                    diag = cur_data['dialogue']
                    diag = [[role, text] for role,text in diag if text]
                    prompt_his = get_all_history_prompt(diag)
                    prompt = instruction + prompt_his
                    medical_records = cur_data['medical_record']
                    for record in medical_records:
                        record = handle_record(record)
                        record_str = json.dumps(record, ensure_ascii=False)
                        writer.write(json.dumps({'input': prompt, 'target':record_str}, ensure_ascii=False) + '\n')
                    
                    line = r.readline()
                    cts += 1
                    print(cts)
                except:
                    cts += 1
                    print(f'error: {cts} {line}')
                    print(cts)
                    line = r.readline()

    # # save_path = data_path[:data_path.rfind('.')] + '_handled.jsonl'
    # # save_error_path = data_path[:data_path.rfind('.')] + '_error.jsonl'
    # # data = readjson(data_path)
    
    # # error_cts = 0
    # # for id, content in tqdm(data.items()):
    # #     try:
    # #         diag = handle_dia(content['dialogue'])
    # #         diag = merge_dia(diag)

    # #         report = content['report']
    # #         cur_res = {'id': id, 'dialogue':diag, 'medical_record': report}
    # #         writer.write(json.dumps(cur_res, ensure_ascii=False) + '\n')
    # #     except:
    # #         error_cts += 1
    # #         print(f'error_cts: {error_cts}, {traceback.format_exc()}')
    # #         writer_error.write(json.dumps({id:content}, ensure_ascii=False) + '\n')
    # # print(f'error_cts: {error_cts}')
    # # if error_cts < 1:
    # #     remove(save_error_path)



if __name__ == '__main__':
    main()