import faiss

def cluster(embeddings, ncentroids=2, niter=20, verbose=True, gpu=True):
    d = embeddings.shape[1]
    kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, gpu=gpu)
    kmeans.train(embeddings)
    return kmeans


def search(data, query, top_k=1):
    dim = query.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(data)
    D, I = index.search(query, top_k)
    return D, I


def handle_centerid_search_res(I, paths):
    # 
    res = {}
    I = I.tolist()
    for i, sub_I in enumerate(I):
        cur = []
        for item in sub_I:
            cur.append(paths[item])
        res[i] = cur
    return res


def handle_embedding_search_res(I, paths):
    res = {}
    I = I.tolist()
    for i, sub_I in enumerate(I):
        center_ids = sub_I[0]
        if center_ids not in res:
            res[center_ids] = []
        res[center_ids].append(paths[i])
    return res





