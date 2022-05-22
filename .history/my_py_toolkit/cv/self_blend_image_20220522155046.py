

import albumentations as A
import albumentations as alb
import cv2
import dlib
import numpy as np

from torchvision.transforms import *
from PIL import Image


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














