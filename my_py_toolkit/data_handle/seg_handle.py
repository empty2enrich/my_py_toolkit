import cv2

def draw_contours(image_path, seg_path, color=[255,255,255], thr=200):
    # 根据分割结果，画框
    img = cv2.imread(image_path)
    #canny
    img_seg = cv2.imread(seg_path, cv2.IMREAD_GRAYSCALE)
    img_seg = cv2.Canny(img_seg, 1, 1)
    # contour
    img[img_seg > thr] = color
    return img