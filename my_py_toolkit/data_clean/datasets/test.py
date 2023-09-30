# from my_py_toolkit.file.toolkit import *
import sys
import json
from tqdm import tqdm

key_mapping = {
    "input": "question",
    "output": "response"
}

def readjson(file_path):
  """"""
  with open(file_path, "r", encoding="utf-8") as f:
    return json.load(f)

def main():
    data_path = sys.argv[1]
    save_path = data_path[:data_path.rfind('.')] + '_process.jsonl'
    writer = open(save_path, 'w', encoding='utf-8')
    for item in tqdm(readjson(data_path)):
        if "instruction" not in item:
            print(item)
        # cur = {}
        # for k,v in item.items():
        #     k = key_mapping.get(k, k)
        #     cur[k] = v
        # writer.write(json.dumps(cur, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()




