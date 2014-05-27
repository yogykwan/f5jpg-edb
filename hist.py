# -*- coding: utf-8 -*-
# -*- by: Yogy Kwan -*-

from PIL import Image
from D import jpegDecoder
import numpy as np
import matplotlib.pyplot as plt

images=['lena_color0','lena_color32','lena_color42','lena_color52']
for name in images:
  imagename=name+'.jpg'
  image=open(imagename,'rb') 
  im=jpegDecoder(image.read())
  im.readHeads()
  im.readImage()
  x=im.coeff
  cnt0=cnt1=cnt2=cnt3=0
  for i in x:
    if i==0: cnt0+=1
    elif i==1: cnt1+=1
    elif i==2: cnt2+=1
    elif i==3: cnt3+=1
  print(cnt0, cnt1, cnt2, cnt3)
  plt.figure(figsize=(7,5))
  n,bins,patches = plt.hist(x,16,histtype='bar',normed=True,range=(-8,8),facecolor='g',alpha=0.75)
  plt.xlabel('DCT Coefficient')
  plt.ylabel('Probability')
  plt.grid(True)
  plt.axis([-8, 8, 0, 1.0])
  #plt.show()
  plt.savefig('hist_'+name+'.png')

