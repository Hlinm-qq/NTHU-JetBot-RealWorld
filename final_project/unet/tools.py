import os
from os.path import splitext
import json
import numpy as np
import torch
from PIL import Image
from multiprocessing import Pool
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from tqdm import tqdm
from functools import partial

def load_image(filename):
    ext = splitext(filename)[1]
    if ext == '.npy':
        return Image.fromarray(np.load(filename))
    elif ext in ['.pt', '.pth']:
        return Image.fromarray(torch.load(filename).numpy())
    else:
        return Image.open(filename)

def unique_mask_values(mask_file):
    mask = np.asarray(load_image(mask_file))
    if mask.ndim == 2:
        return np.unique(mask)
    elif mask.ndim == 3:
        mask = mask.reshape(-1, mask.shape[-1])
        return np.unique(mask, axis=0)
    else:
        raise ValueError(f'Loaded masks should have 2 or 3 dimensions, found {mask.ndim}')

class CustomDataset(Dataset):
    """
    https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
    """
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths, self.mask_paths = self._get_image_paths()
        with Pool() as p:
            unique = list(p.map(partial(unique_mask_values), self.mask_paths))

        self.mask_values = list(sorted(np.unique(np.concatenate(unique), axis=0).tolist()))
    
    def _get_image_paths(self):
        image_paths, mask_paths = [], []
        for dirpath, _, filenames in sorted(os.walk(self.root_dir)):
            if "img.png" in filenames:
                if os.path.isdir(dirpath):
                    image_paths.append(os.path.join(dirpath, "img.png"))
                    mask_paths.append(os.path.join(dirpath, "label.png"))
        return image_paths, mask_paths
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, index):
        image_path, mask_path = self.image_paths[index], self.mask_paths[index]
        image = Image.open(image_path).convert("RGB")
        r, g, b = image.split()
        image = Image.merge("RGB", (b, g, r))
        mask = Image.open(mask_path).convert("RGB").resize((128, 128), resample=Image.NEAREST) 
        r, g, b = mask.split()
        mask = Image.merge("RGB", (b, g, r))
        if self.transform:
            image = self.transform(image)
            mask = torch.from_numpy(np.array(mask)).long()
            mask = torch.argmax(mask, dim=-1)
        return {
            "image": image,
            "mask": mask
        }