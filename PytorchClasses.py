import os
from os import path
import random
import cv2
from tqdm import tqdm
import pickle

import numpy as np
import pandas as pd
import matplotlib as plt
from matplotlib import pyplot
from matplotlib.image import imread
from sklearn.neighbors import NearestNeighbors
import torch
import torchvision
import torch.nn as nn
import torchvision.transforms as transforms
import torch.optim as optim
import matplotlib.pyplot as plt
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision.datasets import ImageFolder
from torch.autograd import Variable

img_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])



class ImageDataset(Dataset):

    def __init__(self,data,transform=img_transform):
        self.data = data
        self.transform = transform
        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self,index):
        if torch.is_tensor(index):
            index = index.tolist()

        item = self.data.iloc[index]
        name = item[1]
        image = item[0]/255
        
        if self.transform:
            sample = self.transform(image)
        
        return np.moveaxis(image,-1,0), name









class Autoencoder(nn.Module):
    def __init__(self):
        super(Autoencoder, self).__init__()
        
        self.Conv1 = nn.Conv2d(3,16,3)
        self.Conv2 = nn.Conv2d(16,32,3)
        self.Conv3 = nn.Conv2d(32,64,7)

        
        self.pool = nn.MaxPool2d(2,2,return_indices=True)
        

        self.ConvTrans3 = nn.ConvTranspose2d(64,32,7)
        self.ConvTrans2 = nn.ConvTranspose2d(32,16,3)
        self.ConvTrans1 = nn.ConvTranspose2d(16,3,3)
        
        self.unpool = nn.MaxUnpool2d(2,2)
        self.sig = nn.Sigmoid()
        
        

    def forward(self, x):
        
        x = self.Conv1(x)
        x = F.relu(x)
        x, indices1 = self.pool(x)
        x = self.Conv2(x)
        x = F.relu(x)
        x, indices2 = self.pool(x)
        x = self.Conv3(x)
        
        x = self.ConvTrans3(x)
        x = self.unpool(x,indices2)
        x = F.relu(x)
        x = self.ConvTrans2(x)
        x = self.unpool(x,indices1)
        x = F.relu(x)
        x = self.ConvTrans1(x)
        x = self.sig(x)
        
        return x
    
    def encode(self,x):
        
        x = self.Conv1(x)
        x = F.relu(x)
        x, indices1 = self.pool(x)
        x = self.Conv2(x)
        x = F.relu(x)
        x, indices2 = self.pool(x)
        x = self.Conv3(x)
        
        return x