import json
from bs4 import BeautifulSoup
from my_py_toolkit.file.file_toolkit import get_file_paths, get_file_name
from tqdm import tqdm
import re

def handle_content(content):
    if not content:
        return ''
    else:
        return content.strip('\n ')

def get_metadata(soup):
    # title
    title = soup.h1.string
    title = handle_content(title)
    # author
    meta_data = soup.find_all('div', 'topic__authors-main-cont')
    if len(meta_data) < 1:
        return '', '', ''
    
    meta_data = meta_data[0]
    author = ''
    for v in meta_data:
        if v.name in ['p', 'strong']:
            author += handle_content(v.string) + ' '
    author = author.replace('作者：', '').strip(' ')
    # date
    # print(meta_data)
    date = meta_data.find_all('div', 'topic__authors')[0].string
    date = handle_content(date)
    date = date.replace('医学审查', '')
    date = handle_content(date)

    return title, author, date

def handle_para(para):
    res = ''
    for v in para.contents:
        if v.name is None:
            res += v.string
        elif v.name in ['span']:
            continue
        else:
            res += handle_para(v)
    res = res.strip('\n ')
    return res

def get_content(soup):
    result = ''
    content = soup.find_all('div', 'topic__accordion')
    if len(content) < 1:
        return ''
    content = content[0]
    paras = content.find_all('div', 'para')
    for p in paras:
        p = handle_para(p)
        if p:
            result += p + '\n'
    return result

def check_para(para):
    if re.match('h.*', para.name):
        return True
    elif para.name == 'div' and 'para' in para.attrs.get('class', ''):
        return True
    else:
        return False

def get_title_weight(title):
    if 'h' in title:
        return 10000 - int(title[1:])
    elif 'b' == title:
        return 1
    return -1

def get_title_relation(cur_title, title):
    cur_weight, weight = get_title_weight(cur_title), get_title_weight(title)
    if cur_weight == weight:
        return 'same'
    elif cur_weight > weight:
        return 'parent'
    else:
        return 'child'


def get_title(para, parent_title):
    if re.match('h.*', para.name) :
        return handle_para(para), get_title_relation(para.name, parent_title), para.name
    else:
        return None, None, None

def get_parent(stack, title_level):
    while stack:
        cur, cur_name , cur_level = stack.pop()
        if get_title_relation(cur_level, title_level) == 'parent':
            return cur, cur_name , cur_level
    return None, None, None

def get_content_dict(soup, title_name):
    result = []
    stack = []
    content = soup.find_all('div', 'topic__accordion')
    if len(content) < 1:
        return ''
    content = content[0]
    paras = content.find_all(['div', re.compile("h.*")])
    parent, parent_title, parent_level = result, title_name, 'h1'
    cur_title = title_name
    cur_content = ''
    cur_level = 'h1'
    for p in paras:
        if not check_para(p):
            continue
        new_title_name, relation_title, new_title_level = get_title(p, cur_level)
        # print(new_title_name, relation_title, new_title_level)
        if new_title_name:
            # print('-' + relation_title + '-')
            if relation_title == 'child':
                if cur_content:
                    pre_result = {cur_title: [{'': cur_content}]}
                else:
                    pre_result = {cur_title: []}

                parent.append(pre_result)
                stack.append([parent[-1][cur_title], parent_title, parent_level])
                parent = pre_result[cur_title]
                parent_title = cur_title
                parent_level = new_title_level
                
                cur_title = new_title_name
                cur_content = ''
                cur_level = new_title_level
            elif relation_title == 'same':
                # print(f'content: {parent, cur_content}')
                if cur_content:
                    pre_result = {cur_title: cur_content}
                    parent.append(pre_result)
                
                cur_title = new_title_name
                cur_content = ''
                cur_level = new_title_level
            elif relation_title == 'parent':
                if cur_content:
                    pre_result = {cur_title: cur_content}
                    parent.append(pre_result)

                parent, parent_title, parent_level = get_parent(stack, new_title_level)

                cur_title = new_title_name
                cur_content = ''
                cur_level = new_title_level
            
            
        else:
            p = handle_para(p)
            if p:
                cur_content += p + '\n'
        
        
    if cur_content:
        pre_result = {cur_title: cur_content}
        parent.append(pre_result)

            
    return result




if __name__ == '__main__':
    data_dir = r'E:\dataset\nlp\MSDZHProfessionalMedicalTopics'
    save_path = './MSDZHProfessionalMedicalTopics.txt'
    save_path_dict = './MSDZHProfessionalMedicalTopics_dict.txt'
    writer = open(save_path, 'w', encoding='utf-8')
    writer_dict = open(save_path_dict, 'w', encoding='utf-8')
    files = get_file_paths(data_dir, ['html'])
    filter_files = ['abbreviations.html', 'about.html']
    for i, file in tqdm(enumerate(files)):
        fn = get_file_name(file)
        # if get_file_name(file) in filter_files:
        #     continue
        if not fn.startswith('{'):
            continue
        # print(file)
        soup = BeautifulSoup(open(file, 'r', encoding='utf-8'), 'html.parser')
        title, author, date = get_metadata(soup)
        content = get_content(soup)
        content_dict = get_content_dict(soup, title)
        cur_res = {
            'id': i,
            'filename': fn,
            'title': title,
            'author': author,
            'date': date,
            'content': content
        }
        writer.write(json.dumps(cur_res, ensure_ascii=False) + '\n')

        cur_res_dict = {
            'id': i,
            'filename': fn,
            'title': title,
            'author': author,
            'date': date,
            'content': content_dict
        }
        writer_dict.write(json.dumps(cur_res_dict, ensure_ascii=False) + '\n')


