from collections import Counter

def static_str(datas, topk=5):
    cts = Counter(datas)
    cts = sorted(cts.items(), key=lambda x:x[1])
    cts = cts[:topk]
    return cts  

def static_dict(datas, topk=5):
    cts = []
    res = {}
    for data in datas:
        # print(f'={data}=')
        for k,v in data.items():
            if k not in res:
                res[k] = [v]
            else:
                res[k].append(v)
    
    for k,v in res.items():
        cur_ct = Counter(v)
        cur_ct = sorted(cur_ct.items(), key=lambda x:x[1])
        cts.append(cur_ct[:topk])
    return cts 

 

def stastic_values(datas, topk=5):
    if not datas:
        return []

    res = []
    if isinstance(datas[0], str):
        return static_str(datas, topk)
    elif isinstance(datas[0], dict):
        return static_dict(datas, topk)
    else:
        raise Exception('Error datatype for counter')