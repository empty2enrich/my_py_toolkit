

import albumentations as A
import albumentations as alb
import cv2
import dlib
import numpy as np
import scipy as sp
import random
import sys
from PIL import Image
from skimage.measure import label, regionprops
from torchvision.transforms import *


def reorder_landmark(landmark):
    landmark_add=np.zeros((13,2))
    for idx,idx_l in enumerate([77,75,76,68,69,70,71,80,72,73,79,74,78]):
        landmark_add[idx]=landmark[idx_l]
    landmark[68:]=landmark_add
    return landmark


def hflip(img,mask=None,landmark=None,bbox=None):
	H,W=img.shape[:2]
	landmark=landmark.copy()
	bbox=bbox.copy()

	if landmark is not None:
		landmark_new=np.zeros_like(landmark)

		
		landmark_new[:17]=landmark[:17][::-1]
		landmark_new[17:27]=landmark[17:27][::-1]

		landmark_new[27:31]=landmark[27:31]
		landmark_new[31:36]=landmark[31:36][::-1]

		landmark_new[36:40]=landmark[42:46][::-1]
		landmark_new[40:42]=landmark[46:48][::-1]

		landmark_new[42:46]=landmark[36:40][::-1]
		landmark_new[46:48]=landmark[40:42][::-1]

		landmark_new[48:55]=landmark[48:55][::-1]
		landmark_new[55:60]=landmark[55:60][::-1]

		landmark_new[60:65]=landmark[60:65][::-1]
		landmark_new[65:68]=landmark[65:68][::-1]
		if len(landmark)==68:
			pass
		elif len(landmark)==81:
			landmark_new[68:81]=landmark[68:81][::-1]
		else:
			raise NotImplementedError
		landmark_new[:,0]=W-landmark_new[:,0]
		
	else:
		landmark_new=None

	if bbox is not None:
		bbox_new=np.zeros_like(bbox)
		bbox_new[0,0]=bbox[1,0]
		bbox_new[1,0]=bbox[0,0]
		bbox_new[:,0]=W-bbox_new[:,0]
		bbox_new[:,1]=bbox[:,1].copy()
		if len(bbox)>2:
			bbox_new[2,0]=W-bbox[3,0]
			bbox_new[2,1]=bbox[3,1]
			bbox_new[3,0]=W-bbox[2,0]
			bbox_new[3,1]=bbox[2,1]
			bbox_new[4,0]=W-bbox[4,0]
			bbox_new[4,1]=bbox[4,1]
			bbox_new[5,0]=W-bbox[6,0]
			bbox_new[5,1]=bbox[6,1]
			bbox_new[6,0]=W-bbox[5,0]
			bbox_new[6,1]=bbox[5,1]
	else:
		bbox_new=None

	if mask is not None:
		mask=mask[:,::-1]
	else:
		mask=None
	img=img[:,::-1].copy()
	return img,mask,landmark_new,bbox_new


def crop_face(img,landmark=None,bbox=None,margin=False,crop_by_bbox=True,abs_coord=False,only_img=False,phase='train'):
	assert phase in ['train','val','test']

	#crop face------------------------------------------
	H,W=len(img),len(img[0])

	assert landmark is not None or bbox is not None

	H,W=len(img),len(img[0])
	
	if crop_by_bbox:
		x0,y0=bbox[0]
		x1,y1=bbox[1]
		w=x1-x0
		h=y1-y0
		w0_margin=w/4#0#np.random.rand()*(w/8)
		w1_margin=w/4
		h0_margin=h/4#0#np.random.rand()*(h/5)
		h1_margin=h/4
	else:
		x0,y0=landmark[:68,0].min(),landmark[:68,1].min()
		x1,y1=landmark[:68,0].max(),landmark[:68,1].max()
		w=x1-x0
		h=y1-y0
		w0_margin=w/8#0#np.random.rand()*(w/8)
		w1_margin=w/8
		h0_margin=h/2#0#np.random.rand()*(h/5)
		h1_margin=h/5

	

	if margin:
		w0_margin*=4
		w1_margin*=4
		h0_margin*=2
		h1_margin*=2
	elif phase=='train':
		w0_margin*=(np.random.rand()*0.6+0.2)#np.random.rand()
		w1_margin*=(np.random.rand()*0.6+0.2)#np.random.rand()
		h0_margin*=(np.random.rand()*0.6+0.2)#np.random.rand()
		h1_margin*=(np.random.rand()*0.6+0.2)#np.random.rand()	
	else:
		w0_margin*=0.5
		w1_margin*=0.5
		h0_margin*=0.5
		h1_margin*=0.5
			
	y0_new=max(0,int(y0-h0_margin))
	y1_new=min(H,int(y1+h1_margin)+1)
	x0_new=max(0,int(x0-w0_margin))
	x1_new=min(W,int(x1+w1_margin)+1)
	
	img_cropped=img[y0_new:y1_new,x0_new:x1_new]
	if landmark is not None:
		landmark_cropped=np.zeros_like(landmark)
		for i,(p,q) in enumerate(landmark):
			landmark_cropped[i]=[p-x0_new,q-y0_new]
	else:
		landmark_cropped=None
	if bbox is not None:
		bbox_cropped=np.zeros_like(bbox)
		for i,(p,q) in enumerate(bbox):
			bbox_cropped[i]=[p-x0_new,q-y0_new]
	else:
		bbox_cropped=None

	if only_img:
		return img_cropped
	if abs_coord:
		return img_cropped,landmark_cropped,bbox_cropped,(y0-y0_new,x0-x0_new,y1_new-y1,x1_new-x1),y0_new,y1_new,x0_new,x1_new
	else:
		return img_cropped,landmark_cropped,bbox_cropped,(y0-y0_new,x0-x0_new,y1_new-y1,x1_new-x1)



class RandomDownScale(alb.core.transforms_interface.ImageOnlyTransform):
	def apply(self,img,**params):
		return self.randomdownscale(img)

	def randomdownscale(self,img):
		keep_ratio=True
		keep_input_shape=True
		H,W,C=img.shape
		ratio_list=[2,4]
		r=ratio_list[np.random.randint(len(ratio_list))]
		img_ds=cv2.resize(img,(int(W/r),int(H/r)),interpolation=cv2.INTER_NEAREST)
		if keep_input_shape:
			img_ds=cv2.resize(img_ds,(W,H),interpolation=cv2.INTER_LINEAR)

		return img_ds

def get_source_transforms():
	return alb.Compose([
			alb.Compose([
					alb.RGBShift((-20,20),(-20,20),(-20,20),p=0.3),
					alb.HueSaturationValue(hue_shift_limit=(-0.3,0.3), sat_shift_limit=(-0.3,0.3), val_shift_limit=(-0.3,0.3), p=1),
					alb.RandomBrightnessContrast(brightness_limit=(-0.1,0.1), contrast_limit=(-0.1,0.1), p=1),
				],p=1),

			alb.OneOf([
				RandomDownScale(p=1),
				alb.Sharpen(alpha=(0.2, 0.5), lightness=(0.5, 1.0), p=1),
			],p=1),
			
		], p=1.)

	
def get_transforms():
	return alb.Compose([
		
		alb.RGBShift((-20,20),(-20,20),(-20,20),p=0.3),
		alb.HueSaturationValue(hue_shift_limit=(-0.3,0.3), sat_shift_limit=(-0.3,0.3), val_shift_limit=(-0.3,0.3), p=0.3),
		alb.RandomBrightnessContrast(brightness_limit=(-0.3,0.3), contrast_limit=(-0.3,0.3), p=0.3),
		alb.ImageCompression(quality_lower=40,quality_upper=100,p=0.5),
		
	], 
	additional_targets={f'image1': 'image'},
	p=1.)


def randaffine(img, mask):
	f=alb.Affine(
			translate_percent={'x':(-0.03,0.03),'y':(-0.015,0.015)},
			scale=[0.95,1/0.95],
			fit_output=False,
			p=1)
		
	g=alb.ElasticTransform(
			alpha=50,
			sigma=7,
			alpha_affine=0,
			p=1,
		)

	transformed=f(image=img,mask=mask)
	img=transformed['image']
	
	mask=transformed['mask']
	transformed=g(image=img,mask=mask)
	mask=transformed['mask']
	return img,mask


def alpha_blend(source,target,mask):
	mask_blured = get_blend_mask(mask)
	img_blended=(mask_blured * source + (1 - mask_blured) * target)
	return img_blended,mask_blured

def dynamic_blend(source,target,mask):
	mask_blured = get_blend_mask(mask)
	blend_list=[0.25,0.5,0.75,1,1,1]
	blend_ratio = blend_list[np.random.randint(len(blend_list))]
	mask_blured*=blend_ratio
	img_blended=(mask_blured * source + (1 - mask_blured) * target)
	return img_blended,mask_blured

def get_blend_mask(mask):
	H,W=mask.shape
	size_h=np.random.randint(192,257)
	size_w=np.random.randint(192,257)
	mask=cv2.resize(mask,(size_w,size_h))
	kernel_1=random.randrange(5,26,2)
	kernel_1=(kernel_1,kernel_1)
	kernel_2=random.randrange(5,26,2)
	kernel_2=(kernel_2,kernel_2)
	
	mask_blured = cv2.GaussianBlur(mask, kernel_1, 0)
	mask_blured = mask_blured/(mask_blured.max())
	mask_blured[mask_blured<1]=0
	
	mask_blured = cv2.GaussianBlur(mask_blured, kernel_2, np.random.randint(5,46))
	mask_blured = mask_blured/(mask_blured.max())
	mask_blured = cv2.resize(mask_blured,(W,H))
	return mask_blured.reshape((mask_blured.shape+(1,)))


def get_alpha_blend_mask(mask):
	kernel_list=[(11,11),(9,9),(7,7),(5,5),(3,3)]
	blend_list=[0.25,0.5,0.75]
	kernel_idxs=random.choices(range(len(kernel_list)), k=2)
	blend_ratio = blend_list[random.sample(range(len(blend_list)), 1)[0]]
	mask_blured = cv2.GaussianBlur(mask, kernel_list[0], 0)
	# print(mask_blured.max())
	mask_blured[mask_blured<mask_blured.max()]=0
	mask_blured[mask_blured>0]=1
	# mask_blured = mask
	mask_blured = cv2.GaussianBlur(mask_blured, kernel_list[kernel_idxs[1]], 0)
	mask_blured = mask_blured/(mask_blured.max())
	return mask_blured.reshape((mask_blured.shape+(1,)))


transforms = get_transforms()
source_transforms = get_source_transforms()


def self_blending(img,landmark):
    H,W=len(img),len(img[0])
    if np.random.rand()<0.25:
        landmark=landmark[:68]
    if exist_bi:
        # logging.disable(logging.FATAL)
        # mask=random_get_hull(landmark,img)[:,:,0]
        # logging.disable(logging.NOTSET)
        pass
    else:
        mask=np.zeros_like(img[:,:,0])
        cv2.fillConvexPoly(mask, cv2.convexHull(landmark), 1.)


    source = img.copy()
    if np.random.rand()<0.5:
        source = source_transforms(image=source.astype(np.uint8))['image']
    else:
        img = source_transforms(image=img.astype(np.uint8))['image']

    source, mask = randaffine(source,mask)

    img_blended,mask= dynamic_blend(source,img,mask)
    img_blended = img_blended.astype(np.uint8)
    img = img.astype(np.uint8)

    return img,img_blended,mask









