from my_py_toolkit.file.file_toolkit import *


def main():
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
    writejson(res, 'labels.json')

if __name__ == '__main__':
    main()