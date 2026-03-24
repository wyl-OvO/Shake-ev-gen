import os
import cv2
import numpy as np
from tqdm import tqdm
from src.config import cfg
from src.simulator import EventSim
from vizvoxel_np import evlist_to_gif,evlist_to_mp4,generate_voxels,generate_masks


def _frame_sort_key(filename):
    stem, _ = os.path.splitext(filename)
    return (0, int(stem)) if stem.isdigit() else (1, stem)



#__从imgs和shaked_imgs批量读取并生成事件_________________
img_dir = 'imgs'
shaked_root = 'shaked_imgs'
ev_root = 'evs'
os.makedirs(ev_root, exist_ok=True)

img_files = sorted(
    [f for f in os.listdir(img_dir) if os.path.splitext(f)[1].lower() in {'.png', '.jpg', '.jpeg', '.bmp'}]
)

sim = EventSim(cfg=cfg)

for img_name in tqdm(img_files, desc='Processing image groups'):
    stem, _ = os.path.splitext(img_name)
    img0path = os.path.join(img_dir, img_name)
    shaked_dir = os.path.join(shaked_root, stem)

    if not os.path.isdir(shaked_dir):
        print(f'Skip {img_name}: {shaked_dir} not found')
        continue

    img0 = cv2.imread(img0path, cv2.IMREAD_GRAYSCALE)
    if img0 is None:
        print(f'Skip {img_name}: failed to read base image')
        continue

    shaked_files = sorted(
        [
            f for f in os.listdir(shaked_dir)
            if os.path.splitext(f)[1].lower() in {'.png', '.jpg', '.jpeg', '.bmp'}
        ],
        key=_frame_sort_key,
    )

    imgs = [img0]
    for shaked_name in shaked_files:
        shaked_path = os.path.join(shaked_dir, shaked_name)
        shaked_img = cv2.imread(shaked_path, cv2.IMREAD_GRAYSCALE)
        if shaked_img is None:
            print(f'Skip frame: failed to read {shaked_path}')
            continue
        imgs.append(shaked_img)

    if len(imgs) < 2:
        print(f'Skip {img_name}: no valid shaked frames in {shaked_dir}')
        continue

    imgs = np.stack(imgs, axis=0)

    # generate_events:
    num_events, num_on_events, num_off_events = 0, 0, 0
    events = []
    start_time_us = 1

    for i in range(0, len(imgs)):
        if i % 1 == 0:  # 隔多少帧取一帧进行仿真
            timestamp_us = start_time_us + 8333 * i  # 120fps对应的帧间隔
            image = imgs[i]

            # event generation!!!
            event = sim.generate_events(image, timestamp_us)

            if event is not None:
                events.append(event)
                num_events += event.shape[0]
                num_on_events += np.sum(event[:, -1] == 1)
                num_off_events += np.sum(event[:, -1] == 0)

    sim.reset()

    if len(events) == 0:
        print(f'Skip {img_name}: no events generated')
        continue

    evpath = os.path.join(ev_root, f'{stem}_ev.npy')
    gifpath = os.path.join(ev_root, f'{stem}.gif')

    events = np.concatenate(events, axis=0)
    print(f'{img_name}: events shape = {events.shape}')
    np.save(evpath, events, allow_pickle=True)  # t,x,y,p

    # 生成可视化
    evlist_to_gif(evpath, gifpath, imgsize=imgs[0].shape)

