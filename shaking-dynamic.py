import os
import numpy as np
import matplotlib.cbook as cbook
import matplotlib.pyplot as plt
import imageio


def shake_imgs(path, path_shaked_imgs, shift):
	ret = os.access(path, os.F_OK)

	if not ret:
		raise FileNotFoundError(f"Input image directory does not exist: {path}")

	f_list = sorted(os.listdir(path))
	if not f_list:
		raise RuntimeError(f"No images found under: {path}")

	num_images = 2

	for j in range(0,len(f_list)):
		if (os.path.isdir(path_shaked_imgs + '/' + f_list[j].split('.')[0]) == False):
			os.mkdir(path_shaked_imgs + '/' + f_list[j].split('.')[0])
		for img in range(0,  num_images):

			with cbook.get_sample_data(path + '/' + f_list[j]) as image_file:
				image = plt.imread(image_file)

				# from top to bottom
				if img==0:
					img_new = np.zeros(image.shape)
					img_new[0:(shift+1), :] = image[0:(shift+1), :]
					img_new[(shift+1):-1:1, :] = image[0:-(shift + 2):1, :]
				# from left to rigth
				elif img==1:
					img_new = np.zeros(image.shape)
					img_new[:, 0:(shift+1)] = image[:, 0:(shift+1)]
					img_new[:, (shift + 1):-1:1] = image[:, 0:-(shift + 2):1]

			# JPEG writer expects integer pixels; normalize float images to uint8.
			if np.issubdtype(img_new.dtype, np.floating):
				img_to_write = np.clip(img_new * 255.0, 0, 255).astype(np.uint8)
			else:
				img_to_write = img_new

			imageio.imwrite(path_shaked_imgs + '/' + f_list[j].split('.')[0] + '/' + str(img) + '.jpg', img_to_write)


def cross_corr():
	pass



if __name__ == "__main__":
	base_dir = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(base_dir, 'imgs')
	path_shaked_imgs = os.path.join(base_dir, 'shaked_imgs')

	shift = 5

	shake_imgs(path, path_shaked_imgs,shift)

print('end')