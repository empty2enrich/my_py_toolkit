# from my_py_toolkit.file.file_toolkit import *
import sys
import json
from tqdm import tqdm
import os
from os import remove
import traceback
import re

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

def handle_record(record, key):
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
    mapping_reserve = {v:k for k,v in mapping.items()}
    
    return record.get(mapping_reserve.get(key, key), '')
    


instruction = '给定医生和患者的对话内容，请生成一份患者的病历信息报告，' \
           '包括{主诉，现病史, 既往史，过敏史，个人史，婚育史，家族史，检查检验结果, 治疗建议}。如果没有则写“无”,并用严格用json格式输出。' \
           "json格式为：{'主诉':''，'现病史':'', '既往史': ''，'过敏史':''，'个人史':''，'婚育史':''，'家族史':''，'检查检验结果':'', '治疗建议':''}。"\
            "医生患者对话内容：\n"

empty_mapping = {
    '主诉': ['无', '暂缺。', '', '暂无。', '无。', '暂缺'],
    '现病史': ['无', '暂缺。', '', '暂无。', '无。', '暂缺'],
    '辅助检查': ['无', '暂缺。', '', '暂无。', '无。', '暂缺'],
    '现病史': ['无', '暂缺。', '', '暂无。', '无。', '暂缺'],
    '现病史': ['无', '暂缺。', '', '暂无。', '无。', '暂缺'],

}


def get_generate_medical_record_prompt_multi(history):
    # history = filter_history(history)
    history_prompt = get_all_history_prompt(history)
    prompts = []
    # prompt = '给定医生和患者的对话内容，请生成一份患者的病历信息报告，' \
    #        '包括{主诉，现病史, 既往史，过敏史，个人史，婚育史，家族史，检查检验结果, 治疗建议}。如果没有则写“无”,并用严格用json格式输出。' \
    #        "json格式为：{'主诉':''，'现病史':'', '既往史': ''，'过敏史':''，'个人史':''，'婚育史':''，'家族史':''，'检查检验结果':'', '治疗建议':''}。"\
    #         "医生患者对话内容：\n"
    # prompts.append(prompt)
    # prompt = '给定医生和患者的对话内容，请生成一份患者的问诊的信息报告，' \
    #        '包括{主诉，现病史，过敏史，个人史，婚育史，家族史，检查检验结果}。如果没有则写“无”,并用严格用json格式输出。' \
    #        "json格式为：{'主诉':''，'现病史':''，'过敏史':''，'个人史':''，'婚育史':''，'家族史':''，'检查检验结果':''}" + "\n" \
    #     "关键信息解释：" \
    #     "主诉通常是指患者在就医时所描述的他们的症状、不适或健康问题。这是患者在对医生进行初诊时提出的问题，是他们希望解决的主要健康问题。在这个情景下，患者的主诉是头疼和发热。" \
    #     "；现病史指的是患者当前正在经历的疾病情况的描述。它包括症状的起始时间、症状的性质、症状的持续时间以及可能的伴随症状。" \
    #     "；过敏史指的是患者对特定物质或环境因素产生过敏反应的历史。这些过敏原可以包括食物、药物、花粉、宠物毛发等。在这个情景下，患者提到他有花粉过敏史，表示他对花粉过敏。" \
    #     "；个人史包括有关患者个人生活和健康的历史信息，通常包括个人的生活习惯和行为，如饮酒、吸烟、锻炼、饮食习惯等。在这个情景下，患者没有提到具体的个人史，因此标注为'无'。" \
    #     "；婚育史指的是有关患者与婚姻、生育和家庭计划相关的历史和信息。包括婚姻状态、婚姻历史、生育历史等。在这个情景下，患者没有提到具体的婚育史，因此标注为'无'。" \
    #     "；家族史指的是有关患者直系亲属和近亲属的健康历史信息，具体包括家庭成员的健康状况。在这个情景下，患者没有提到具体的家族史，因此标注为'无'。" \
    #     "；检查检验结果指的是患者的检查和检验结果，包括各种医学测试和检查所得到的数据，用于评估患者的生理状况、疾病诊断和治疗进展。在这个情景下，患者表示暂时没有进行过体检或其他相关的检查，因此标注为'暂时没有'。" \
    #     "\n" \
    #     '医生和患者的对话内容为：'
    # prompts.append(prompt)

    # v1： 效果还行
    # prompt = '给定医生和患者的对话内容，提取患者的主诉，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    # "{'主诉': ''},"\
    # ' 格式返回数据。'\
    #          "；主诉通常是指患者在就医时所描述的他们的症状、不适或健康问题。这是患者在对医生进行初诊时提出的问题，是他们希望解决的主要健康问题。" \
    #         "医生和患者的对话内容为："
    # 指促使患者就诊的主要症状（或体征）及持续时间。
    # v2、效果不错
    # prompt = '你是一个专业医生，根据给定医生和患者的对话内容，执行以下操作：' \
    #          '1、提取医生患者对话内容中患者就诊的主要症状（或体征、不适，患者在就医时所描述的他们的症状）及持续时间或健康问题，' \
    #          '2、根据步骤 1 的结果，提取患者的主诉，主诉内容必须小于 15 个字，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    # "{'主诉': ''}。"\
    #          "；主诉通常是指促使患者就诊的主要症状（或体征、不适，患者在就医时所描述的他们的症状）及持续时间或健康问题。" \
    #         "医生和患者的对话内容为："
    prompt = '你是一个专业医生，根据给定医生和患者的对话内容，执行以下操作：' \
             '1、提取医生患者对话内容中患者就诊的主要症状（或体征、不适，患者在就医时所描述的他们的症状）及持续时间或健康问题，' \
             '2、根据步骤 1 的结果，提取患者的主诉，主诉内容必须小于 15 个字，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    "{'主诉': ''}。"\
             "；主诉通常是指促使患者就诊的主要症状（或体征、不适，患者在就医时所描述的他们的症状）及持续时间或健康问题。" \
            "医生和患者的对话内容为："
    # prompt = '你是一个专业医生，根据给定医生和患者的对话内容，执行以下操作：' \
    #          '1、提取医生患者对话内容中患者就诊的主要症状（或体征、不适，患者在就医时所描述的他们的症状），' \
    #          '2、根据步骤 1 的结果,严格用json格式输出。 json 格式为: ' \
    # "{'主要症状': []}。"\
    #         "医生和患者的对话内容为："
    prompts.append(prompt)
    prompt = '你是一个专业医生，根据给定医生和患者的对话内容，执行以下操作：' \
             '1、客观的提取医生患者对话内容中，患者本次疾病的发生、演变、诊疗等方面的详细情况，应当按时间顺序书写。内容包括发病情况、主要症状特点及其发展变化情况、伴随症状、发病后诊疗经过及结果、睡眠和饮食等一般情况的变化，以及与鉴别诊断有关的阳性或阴性资料等。' \
             '2、根据步骤 1 的结果，提取患者的现病史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    "{'现病史': ''}。"\
             "；现病史是指患者本次疾病的发生、演变、诊疗等方面的详细情况，应当按时间顺序书写。内容包括发病情况、主要症状特点及其发展变化情况、伴随症状、发病后诊疗经过及结果、睡眠和饮食等一般情况的变化，以及与鉴别诊断有关的阳性或阴性资料等。"\
"①.发病情况：记录发病的时间、地点、起病缓急、前驱症状、可能的原因或诱因。"\
   "②.主要症状特点及其发展变化情况：按发生的先后顺序描述主要症状的部位、性质、持续时间、程度、缓解或加剧因素，以及演变发展情况。"\
    "③.伴随症状：记录伴随症状，描述伴随症状与主要症状之间的相互关系。"\
    '④.发病以来诊治经过及结果：记录患者发病后到入院前，在院内、外接受检查与治疗的详细经过及效果。对患者提供的药名、诊断和手术名称需加引号（“”）以示区别。'\
    "⑥.发病以来一般情况：简要记录患者发病后的精神状态、睡眠、食欲、大小便、体重等情况。" \
            "医生和患者的对话内容为："
    prompts.append(prompt)
    prompt = '给定医生和患者的对话内容，提取患者的既往史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    "{'既往史': ''},"\
    ' 格式返回数据。'\
             "；既往史指患者过去的健康和疾病情况。内容包括既往一般健康状况、疾病史、传染病史、预防接种史、手术外伤史、输血史等。" \
            "医生和患者的对话内容为："
    prompts.append(prompt)
    prompt = '给定医生和患者的对话内容，提取患者的过敏史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    '{"过敏史": ""},'\
    ' 格式返回数据。'\
             "；过敏史指的是患者对特定物质或环境因素产生过敏反应的历史。这些过敏原可以包括食物、药物、花粉、宠物毛发等。" \
            "医生和患者的对话内容为："
    # v1 效果不错
    # prompts.append(prompt)
    # prompt = '给定医生和患者的对话内容，提取患者的个人史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    # '{"个人史": ""},'\
    # ' 格式返回数据。'\
    #          "；个人史包括有关患者个人生活和健康的历史信息，通常包括患者的生活习惯和行为，如饮酒、吸烟、锻炼、饮食习惯等。" \
    #         "医生和患者的对话内容为："
    # prompts.append(prompt)
    prompt = '给定医生和患者的对话内容，执行以下操作：' \
             '1、根据医生和患者的对话内容，提取患者的个人生活和健康的历史信息，通常包括患者的生活习惯和行为，如饮酒、吸烟、锻炼、饮食习惯等。' \
             '2、根据步骤 1 ，提取患者的个人史，个人史的内容为一段文本，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    '{"个人史": "content"},'\
    ' 格式返回数据。'\
            "医生和患者的对话内容为："
    prompts.append(prompt)
    prompt = '给定医生和患者的对话内容，提取患者的婚育史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    "{'婚育史': ''},"\
    ' 格式返回数据。'\
             "；婚育史指的是婚姻状况、结婚年龄、配偶健康状况、有无子女等。女性患者记录初潮年龄、行经期天数 、间隔天数、末次月经时间（或闭经年龄），月经量、痛经及生育等情况。" \
            "医生和患者的对话内容为："
    prompts.append(prompt)
    # prompt = '给定医生和患者的对话内容，提取患者的家族史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    #          "{'家族史': ''}," \
    #          ' 格式返回数据。' \
    #          "；家族史指的是有关患者直系亲属和近亲属的健康历史信息，具体包括家庭成员的健康状况。在这个情景下，患者没有提到具体的家族史，因此标注为'无'。" \
    #         "医生和患者的对话内容为："
    # v1 效果还行
    # prompt = '给定医生和患者的对话内容，提取患者的家族史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
    #          "{'家族史': ''}," \
    #          ' 格式返回数据。' \
    #          "；家族史指的是患者的父母、兄弟、姐妹健康状况，有无与患者类似疾病，有无家族遗传倾向的疾病等。" \
    #         "医生和患者的对话内容为："
    # 效果不错 v2
    prompt = '给定医生和患者的对话内容，执行以下操作：' \
             '1、提取对话内容中提到的患者亲属（父母、父亲、母亲、兄弟、姐妹等）信息，\n' \
             '2、判断步骤 1 提取的患者亲属信息中，有无与患者类似疾病、病史，有无家族遗传倾向的疾病等。' \
             '3、根据步骤 2 的结果，提取患者的家族史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
             "{'家族史': ''}," \
             ' 格式返回数据。' \
             "；家族史指的是患者的父母、兄弟、姐妹等亲属，有无与患者类似疾病，有无家族遗传倾向的疾病等。" \
            "医生和患者的对话内容为："
    prompt = '给定医生和患者的对话内容，执行以下操作：' \
             '1、提取对话内容中提到的患者亲属（父母、父亲、母亲、兄弟、姐妹等）信息，\n' \
             '2、判断步骤 1 提取的患者亲属信息中，有无与患者类似疾病、病史，有无家族遗传倾向的疾病等。' \
             '3、根据步骤 2 的结果，提取患者的家族史，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
             "{'家族史': ''}," \
             ' 格式返回数据。' \
             "；家族史指的是患者的父母、兄弟、姐妹等亲属，有无与患者类似疾病，有无家族遗传倾向的疾病等。" \
            "医生和患者的对话内容为："
    prompts.append(prompt)
    prompt = '给定医生和患者的对话内容，提取患者的检查检验结果，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
             "{'检查检验结果': ''}," \
             ' 格式返回数据。' \
             "；检查检验结果指的是患者的检查和检验结果，包括各种医学测试和检查所得到的数据，用于评估患者的生理状况、疾病诊断和治疗进展。在这个情景下，患者表示暂时没有进行过体检或其他相关的检查，因此标注为'暂时没有'。" \
            "医生和患者的对话内容为："
    prompts.append(prompt)
    prompt = '给定医生和患者的对话内容，提取患者的治疗建议，如果没有则写“无”,并用严格用json格式输出。 json 格式为: ' \
             "{'治疗建议': ''}," \
             ' 格式返回数据。' \
             "；治疗建议是由专业医疗保健提供者，如医生、心理医生、物理治疗师等，向患者提供的关于诊断、治疗和康复的专业建议。这些建议是基于对患者病情、症状和生活状况的综合评估，并旨在制定一个个性化的治疗计划，以最大程度地促进患者的康复和健康。'。" \
            "医生和患者的对话内容为："
    prompts.append(prompt)
    result = []
    for prompt in prompts:
        # print(f'prompt history {len(history_prompt)}: {history_prompt}')
        # if len(history_prompt) > 4000 - len(prompt):
        #     history_prompt = history_prompt[-(4000 - len(prompt)):]
        prompt += history_prompt
        # print(f'prompt {len(prompt)}: {prompt}')
        result.append(prompt)
    # print(result)
    return result


def get_file_name(file_path):
  """
  Get file name.
  Anther implement: os.path.split(file_path)[-1]
  Args:
    file_path:

  Returns:

  """
  return re.split("\\\\|/", file_path)[-1]

def get_wirter(keys, data_path, save_dir='./finetune2'):
    res = []
    fn = get_file_name(data_path)
    os.makedirs(save_dir, exist_ok=True)
    for k in keys:
        fn_k = fn[:fn.rfind('.')] + f'_{k}.jsonl'
        res.append(open(os.path.join(save_dir, fn_k), 'w', encoding='utf-8'))
    return res

def main():
    data_paths = sys.argv[1:]
    keys = '主诉，现病史， 既往史，过敏史，个人史，婚育史，家族史，检查检验结果，治疗建议'.split('，')
    
    for data_path in data_paths:
        writers = get_wirter(keys, data_path, './finetune_v2')
    # result = [[] for _ in range(len(keys))]
        # writer_error = open(save_error_path, 'w', encoding='utf-8')
        cts = 0
        with open(data_path, 'r', encoding='utf-8') as r:
            line = r.readline()
            while line:
                try:
                    cur_data = json.loads(line)
                    diag = cur_data['dialogue']
                    diag = [[role, text] for role,text in diag if text]
                    prompts = get_generate_medical_record_prompt_multi(diag)
                    for i, prompt in enumerate(prompts):
                        medical_records = cur_data['medical_record']
                        for record in medical_records:
                            cur_key_record = {keys[i]: handle_record(record, keys[i])}
                            record_str = json.dumps(cur_key_record, ensure_ascii=False)
                            writers[i].write(json.dumps({'input': prompt, 'target':record_str}, ensure_ascii=False) + '\n')
                    
                    line = r.readline()
                    cts += 1
                    print(cts)
                except:
                    cts += 1
                    print(f'error: {cts} {line}')
                    print(cts)
                    line = r.readline()



if __name__ == '__main__':
    main()