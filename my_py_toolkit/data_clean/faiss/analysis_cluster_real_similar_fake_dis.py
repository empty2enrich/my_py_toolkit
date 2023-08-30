import faiss
import numpy as np
from my_py_toolkit.file.file_toolkit import *
from tqdm import tqdm
from my_py_toolkit.decorator.decorator import fn_timer



def check_line_nums(cts, line_nums):
    if line_nums < 0:
        return True
    
    if cts < line_nums:
        return True
    
    return False

def read_lines(path, line_nums=-1):
    result = []
    with open(path, 'r') as r:
        line = r.readline()
        cts = 0
        while line:
            if not check_line_nums(cts, line_nums):
                break
            
            line = line.strip('\n')
            result.append(line)

            line = r.readline()
            cts += 1
    return result

@fn_timer()
def read_datas(paths, line_nums=-1):
    res = []
    for path in paths:
        res.extend(read_lines(path, line_nums))
    return res

@fn_timer()
def handle_data(data, labels):
    paths_real, embeddings_real, paths_fake, embeddings_fake = [], [], [], []
    for line in tqdm(data):
        path, embedding = line.split(' ')[:2]
        embedding = embedding.split(',')
        embedding = np.asarray([float(v) for v in embedding])
        if labels[path] == 0:
            paths_real.append(path)
            embeddings_real.append(embedding)
        else:
            paths_fake.append(path)
            embeddings_fake.append(embedding)
    
    embeddings_real = np.asarray(embeddings_real).astype(np.float32)
    embeddings_fake = np.asarray(embeddings_fake).astype(np.float32)

    return paths_real, embeddings_real, paths_fake, embeddings_fake

def cluster(embeddings, ncentroids=2, niter=20, verbose=True):
    d = embeddings.shape[1]
    kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=True)
    kmeans.train(embeddings)
    return kmeans

@fn_timer()
def search(data, query, top_k=1):
    dim = query.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(data)
    D, I = index.search(query, top_k)
    return D, I

@fn_timer()
def handle_centerid_search_res(I, D, paths):
    # 
    res = {}
    I = I.tolist()
    D = D.tolist()
    for i, sub_I in enumerate(I):
        cur = []
        for j, item in enumerate(sub_I):
            cur.append((paths[item], D[i][j]))
        res[i] = cur
    return res

@fn_timer()
def handle_embedding_search_res(I, D, paths_real, paths_fake):
    res = {}
    I = I.tolist()
    D = D.tolist()
    for i, sub_I in enumerate(I):
        print(f'D i: {D[i]}')
        real_path = paths_real[i]
        fake_ids = sub_I[0]
        if real_path not in res:
            res[real_path] = []
        res[real_path].append((paths_fake[fake_ids], D[i][0]))
    return res


def get_labels():
    label_dir = '/home/algtest/archive/20230523/dataset/train'
    label_files = ['real_all_label.txt', '224_real_0.8_label.txt',
                'hnbank_0.8_label.txt', 'real_gz_0.8_label.txt',
                'gk_deepfake_500_label.txt', 'gk_ps_150.0_label.txt',
                'luoyan_0613_label.txt', 'll_collect_0613_label.txt', #'xiazheng_0612_train_label',
                'ly_0614_am_train_label.txt', 'ly_0614_bm_train_label.txt',
                'll_0615_real_label.txt',
                'ly_0615_png_label.txt', 'ly_0615_jpg_label.txt', 'll_0615_png_label.txt', 'll_0615_jpg_label.txt',
                'll_0616_mi11pro_jpg_normal_label.txt', 'll_0616_mi11pro_png_normal_label.txt',
                'ly_0616_jpg_normal_label.txt', 'ly_0616_png_normal_label.txt',
                'ljj_0616_mi11pro_train_label.txt', 'ly_0616_mi11pro_jpg_train_label.txt',
                'll_0621_jpg_normal_label.txt', 'll_0621_png_normal_label.txt',
                '0622_applescreen_normal_jpg_label.txt', '0622_applescreen_normal_png_label.txt', 'lcl_0620_jpg_normal_label.txt', 'lcl_0620_png_normal_label.txt',
                'mate10mi11proscreenJpg_normal_label.txt',  'mate10mi11proscreenPng_normal_label.txt', 'mate10mi11proscreenJpg2_normal_label.txt',
                '0627_mate10mi11proscreenJpg_normal_label.txt', '0627_2_mate10mi11proscreenJpg_normal_label.txt', '0627_applescreen_normal_label.txt',  
                '0629_applescreen_normal_label.txt',
                '0703_screen_label.txt',
                '0704_label.txt',
                '0705_Mi11prolegiony7000pjpg_normal_label.txt',
                'real_dawei_20230628_normal_label.txt',  'train_0628_label.txt',
                '0706_fake_screen_label.txt', '0706_real_label.txt',
                '0707_screen_label.txt',
                '0712_screen_label.txt',
                '0713_paper_label.txt', '0713_screen_label.txt',
                '0714_fake_label.txt',
#                'shine_real_label.txt', 'shine_fake_label.txt', 'shine_927_fake_label.txt', 
                'Silentliving_all_label.txt', 'deepfake_label.txt']

    res = {}
    for file in label_files:
        data = read_file(os.path.join(label_dir, file), '\n')
        for line in data:
            if not line:
                continue

            path, label = line.split(' ')
            res[path] = int(label)
    return res


def main():
    data_paths = ['/home/deepteam/ll/github/RECCE-nx/features/recce_trainset_features_scores.txt']
    centroids_path = 'recce_trainset_features_scores_cluster_6.txt'
    centerids_num = 6

    labels = readjson('./labels.json')
    data = read_datas(data_paths)
    paths_real, embeddings_real, paths_fake, embeddings_fake = handle_data(data, labels)

    # kmeans = cluster(embeddings)
    # centerids = np.load(centroids_path + '.npy')

    # center_ids result
    D, I = search(embeddings_fake, embeddings_real, top_k=1)
    centerids_res = handle_embedding_search_res(I, D, paths_real, paths_fake)
    writejson(centerids_res, './real_similarest_fake_res.json')


if __name__ == '__main__':
    main()