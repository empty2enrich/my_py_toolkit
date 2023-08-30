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
def handle_data(data):
    paths, embeddings = [], []
    for line in tqdm(data):
        path, embedding = line.split(' ')[:2]
        embedding = embedding.split(',')
        embedding = np.asarray([float(v) for v in embedding])
        paths.append(path)
        embeddings.append(embedding)
    
    embeddings = np.asarray(embeddings).astype(np.float32)

    return paths, embeddings

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
def handle_embedding_search_res(I, D, paths):
    res = {}
    I = I.tolist()
    D = D.tolist()
    for i, sub_I in enumerate(I):
        print(f'D i: {D[i]}')
        center_ids = sub_I[0]
        if center_ids not in res:
            res[center_ids] = []
        res[center_ids].append((paths[i], D[i][0]))
    return res


def main():
    data_paths = ['/home/deepteam/ll/github/RECCE-nx/features/recce_trainset_features_scores.txt']
    centroids_path = 'recce_trainset_features_scores_cluster_6.txt'
    centerids_num = 6

    data = read_datas(data_paths)
    file_paths, embeddings = handle_data(data)

    # kmeans = cluster(embeddings)
    centerids = np.load(centroids_path + '.npy')

    # center_ids result
    D, I = search(embeddings, centerids, top_k=10000)
    centerids_res = handle_centerid_search_res(I, D, file_paths)
    writejson(centerids_res, './centerids_res.json')

    # embedding search
    D, I = search(centerids, embeddings, top_k=1)
    embedding_res = handle_embedding_search_res(I, D, file_paths)
    writejson(embedding_res, './embedding_res.json')







if __name__ == '__main__':
    main()