import numpy as np
import os
import sys
import pandas
from functools import partial
from t5 import t5_encode_text, t5_tokenize, t5_encode_tokenized_text
from multiprocessing import Pool, cpu_count


t5_name = 't5-large'
return_attn_mask = True

encode_text = partial(t5_encode_text, name = t5_name, return_attn_mask=return_attn_mask)

def make_path_legal(file_path):
  """"""
  if os.path.dirname(file_path) and not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))

def tensor2numpy(tensor):
   tensor = tensor.detach().cpu().numpy()
   return tensor

def embedding_save(embedding, mask, save_path):
   np.savez(save_path, embedding=embedding, attention_mask=mask)

def get_batch_data(start, batch, df, keys):
    sample_ids, texts = [], []
    for j in range(batch):
        sample_id, text = [df.loc[start + j][k] for k in keys]
        sample_ids.append(sample_id)
        texts.append(text)
    
    embedding, mask = encode_text(texts)
    embedding = tensor2numpy(embedding)
    mask = tensor2numpy(mask)
    return sample_ids, embedding, mask


def main():
    # 读取数据
    csv_dir, save_dir = sys.argv[1:3]

    # text 转 embedding
    # 多线程
    keys = ['SAMPLE_ID', 'TEXT']
    batch = 64

    for file in os.listdir(csv_dir):
       file_path = os.path.join(csv_dir, file)
       df = pandas.read_csv(file_path)
       row_nums, column_nums = df.shape

       for i in range(0, row_nums, batch):
            result = []
            sample_ids, embeddings, masks = get_batch_data(i, batch, df, keys)
            with Pool(cpu_count()) as p:
                for sample_id, embed, mask in zip(sample_ids, embeddings, masks):
                    save_path = os.path.join(save_dir, f'{sample_id}.npz')
                    make_path_legal(save_path)
                    result.append(p.apply_async(embedding_save, (embed, mask, save_path)))

                p.close()
                p.join()
                for i in result:
                    print(i.get())



if __name__ == '__main__':
    main()



