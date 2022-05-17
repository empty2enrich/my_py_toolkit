
import cv2
import numpy as np
from PIL import Image

# 图像融合
def get_mask(seg, seg_ids=None):
    mask = np.zeros(seg.shape)
    if not seg_ids:
        seg_ids = set(seg.flatten()) - {0, 255}
    for v in seg_ids:
        mask += seg == v
    return mask.astype(bool)



def merge_picture(source, target, source_seg, imsize=256, seg_ids=None):
    """
    通过分割图 seg, 把原图（source） seg 对应位置替换到目标图像（target）
    Args:
        source (str): 文件路径
        target (str): 目标文件路径
        source_seg (str): 源文件 segmention 路径
        imsize (int, optional): _description_. Defaults to 256.
        seg_ids (set, optional): 需要保留的 segmention ids. Defaults to None.

    Returns:
        img(Image): 合成图。
    """

    source, target, seg = [Image.open(p) for p in [source, target, source_seg]]
    source = source.resize((imsize, imsize), Image.BILINEAR)
    target = target.resize((imsize, imsize), Image.BILINEAR)
    seg = seg.resize((imsize, imsize), Image.BILINEAR)
    seg = seg.convert("P")
    target = target.resize(source.size)
    
    seg_np = np.asarray(seg)
    sour_np = np.asarray(source)
    targ_np = np.asarray(target)
    
    mask = get_mask(seg_np, seg_ids)[..., None]
    # merge
    new_img = sour_np * mask + targ_np * ~ mask
    new_img = Image.fromarray(new_img, mode='RGB')
    return new_img

def warp_img(img, M, shape):
    # 图像对齐
    output_img = np.zeros(shape, dtype=img.dtype)
    cv2.warpAffine(img,
                   M[:2],
                   (shape[1], shape[0]),
                   dst=output_img,
                   borderMode=cv2.BORDER_TRANSPARENT,
                   flags=cv2.WARP_INVERSE_MAP)
    return output_img


