import cv2        
import os
import numpy as np
import os
import re
import torch
from PIL import Image

def normalize(img):
    img = img.astype(np.float32)
    img = (img - np.min(img)) / (np.max(img) - np.min(img))
    return img

def generate_evvoxel(x,y,t,p):
    imgsize =(720,1280)
    evvoxel_p = torch.zeros(imgsize, dtype=torch.float32)
    evvoxel_n = torch.zeros(imgsize, dtype=torch.float32)
        
    x1 = x
    y1 = y
    # t1 = t
    p1 = p
    
    x1 = torch.from_numpy(x1.astype(np.int16)).long()
    y1 = torch.from_numpy(y1.astype(np.int16)).long()
    # t1 = torch.from_numpy(t1).float()
    p1 = torch.from_numpy(p1.astype(np.int16)).float() 
    
    posidx = p1>0;negidx = p1<=0
    
    x1_p = x1[posidx];y1_p = y1[posidx];p1_p = p1[posidx]
    x1_n = x1[negidx];y1_n = y1[negidx];p1_n = p1[negidx]
    
    evvoxel_p.index_put_((y1_p, x1_p), p1_p, accumulate=False)
    evvoxel_n.index_put_((y1_n, x1_n), p1_n+1, accumulate=False)
    return evvoxel_p,evvoxel_n

def generate_evvoxel_PandN(x,y,t,p,imgsize=(160,160)):
    #(180,240)#(720,1280)
    evvoxel = torch.zeros(imgsize, dtype=torch.float32)

    x1 = x
    y1 = y
    # t1 = t
    p1 = p*2-1
    
    total = len(x)
    for i in range(total//1000):
        
        x_ = torch.from_numpy(x1[i*1000:(i+1)*1000].astype(np.int16)).long()
        y_ = torch.from_numpy(y1[i*1000:(i+1)*1000].astype(np.int16)).long()
        # t1 = torch.from_numpy(t1).float()
        p_ = torch.from_numpy(p1[i*1000:(i+1)*1000].astype(np.int16)).float() 
    
        evvoxel.index_put_((y_, x_), p_, accumulate=False)
        
    return evvoxel

def generate_evvoxel_count(x,y,t=None,p=None,imgsize=(160,160)):
    #(180,240)#(720,1280)
    evvoxel = torch.zeros((imgsize[0],imgsize[1]), dtype=torch.float32)
    x = torch.tensor(x)
    y = torch.tensor(y)
    #分别映射正负事件：
    # evvoxel = torch.zeros((2,imgsize[0],imgsize[1]), dtype=torch.float32)
    # idx = p>0;idx_ = p==0
    # evvoxel[0].index_put_((y[idx], x[idx]), 1, accumulate=True)
    # evvoxel[1].index_put_((y[idx_], x[idx_]), 1, accumulate=True)

    #正负一起映射：
    evvoxel.index_put_((y, x), torch.tensor(1.), accumulate=True)
    return evvoxel



def colormap(img):
    color_map = {
    -1: [255, 0, 0],  # 蓝色 (BGR格式)
     0: [255, 255, 255],  # 白色
     1: [0, 0, 255]   # 红色
    }

    # 创建一个新的 RGB 图像
    height, width = img.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

    # 填充 RGB 图像
    for value, color in color_map.items():
        rgb_image[img == value] = color
    return rgb_image

def evlist_to_gif(filepath,outpath,imgsize=(160,160)):
    evarray = np.load(filepath,allow_pickle=True)
    t = evarray[:,0];t = t-t[0]
    x = evarray[:,1]
    y = evarray[:,2]
    p = evarray[:,3]
    
   
    fnum=100
    tgap = t.max()//fnum
    framegap = t.max()//20#t.max()//300#
    evvoxels = []
    for i in range(fnum):
        t1 = i*tgap
        t2 = i*tgap+framegap
            
        idx = np.where((t>t1)&(t<t2))
        x_,y_,t_,p_ = x[idx],y[idx],t[idx],p[idx]
        evvoxel = generate_evvoxel_PandN(x_,y_,t_,p_,imgsize=imgsize)
        evvoxels.append(colormap(evvoxel.numpy()))
        # cv2.imwrite(f'datageneration\\visualize_imgs\\{i}.png',colormap(evvoxel.numpy()))
    images = [Image.fromarray(voxel) for voxel in evvoxels]

    # 将图像列表保存为 GIF 动画
    images[0].save(
        outpath,  # 输出文件名
        save_all=True,  # 保存所有帧
        append_images=images[1:],  # 除第一帧外的其他帧
        duration=200,  # 每帧持续时间（毫秒）
        loop=0  # 循环次数，0 表示无限循环
    )
def evlist_to_mp4(filepath,outpath,imgsize=(160,160),fnum=100):
    evarray = np.load(filepath)
    t = evarray[:,0];t = t-t[0]
    x = evarray[:,1]
    y = evarray[:,2]
    p = evarray[:,3]
    

    tgap = t.max()//fnum
    framegap = t.max()//20#t.max()//300#
    evvoxels = []
    for i in range(fnum):
        t1 = i*tgap
        t2 = i*tgap+framegap
            
        idx = np.where((t>t1)&(t<t2))
        x_,y_,t_,p_ = x[idx],y[idx],t[idx],p[idx]
        evvoxel = generate_evvoxel_PandN(x_,y_,t_,p_,imgsize=imgsize)
        evvoxels.append(colormap(evvoxel.numpy()))
        # cv2.imwrite(f'datageneration\\visualize_imgs\\{i}.png',colormap(evvoxel.numpy()))
    images = [Image.fromarray(voxel) for voxel in evvoxels]

    width,height = images[0].size
    out = cv2.VideoWriter(outpath, cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))

    for img in images:
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)  # 写入帧
    out.release()
def imgs_to_gif(imgs,outpath):

    images = [Image.fromarray(img) for img in imgs[::5]]
    
    images[0].save(
        outpath,  # 输出文件名
        save_all=True,  # 保存所有帧
        append_images=images[1:],  # 除第一帧外的其他帧
        duration=200,  # 每帧持续时间（毫秒）
        loop=0  # 循环次数，0 表示无限循环
    )
    
def generate_voxels(filepath,outpath,imgsize=(160,160)):
    evarray = np.load(filepath)
    t = evarray[:,0];t = t-t[0]
    x = evarray[:,1]
    y = evarray[:,2]
    p = evarray[:,3]
    
   
    fnum=20
    tgap = t.max()//fnum
    framegap = t.max()//fnum#t.max()//300#
    evvoxels = []
    for i in range(fnum):
        t1 = i*tgap
        t2 = i*tgap+framegap
            
        idx = np.where((t>t1)&(t<t2))
        x_,y_,t_,p_ = x[idx],y[idx],t[idx],p[idx]
        evvoxel = generate_evvoxel_count(x_,y_,t_,p_,imgsize=imgsize)
        evvoxels.append(evvoxel.numpy())
    evvoxels = np.stack(evvoxels)
    np.save(outpath,evvoxels)
def generate_masks(filepath,outpath,imgsize=(160,160)):
    evarray = np.load(filepath)
    l = len(evarray)//4
    x = evarray[:l,1]
    y = evarray[:l,2]
    mask = generate_evvoxel_count(x,y,imgsize=imgsize)
    np.save(outpath,mask.bool())
        
    
    

if __name__ == '__main__':
    filepath = r'datageneration/dataset/events/00000000.npy'
    outpath = r"datageneration/dataset/visualize/00000000.gif"
    evlist_to_gif(filepath,outpath)