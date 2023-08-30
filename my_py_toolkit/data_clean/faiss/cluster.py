import faiss
import numpy as np
from my_py_toolkit.file.file_toolkit import *
from my_py_toolkit.decorator.decorator import fn_timer
from tqdm import tqdm


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
    for line in tqdm(data, desc='Reading Data'):
        path, embedding = line.split(' ')[:2]
        embedding = embedding.split(',')
        embedding = np.asarray([float(v) for v in embedding])
        paths.append(path)
        embeddings.append(embedding)
    
    embeddings = np.asarray(embeddings).astype(np.float32)

    return paths, embeddings

@fn_timer()
def cluster(embeddings, ncentroids=2, niter=20, verbose=True):
    d = embeddings.shape[1]
    kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=True, max_points_per_centroid=1000000)
    kmeans.train(embeddings)
    return kmeans


def search(data, query, top_k=1):
    dim = query.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(data)
    D, I = index.search(query, top_k)
    return D, I


def main():
    data_paths = ['/home/deepteam/ll/github/RECCE-nx/features/recce_trainset_features_scores.txt']
    centroids_path = 'recce_trainset_features_scores_cluster_6.txt'

    data = read_datas(data_paths)
    file_paths, embeddings = handle_data(data)

    kmeans = cluster(embeddings, 6)
    np.save(centroids_path, kmeans.centroids)






if __name__ == '__main__':
    main()