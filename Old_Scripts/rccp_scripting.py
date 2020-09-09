#!/usr/bin/env python
# coding: utf-8

# In[1]:
import pandas as pd
import numpy as np
import os
import csv
from itertools import chain
import xlrd
import glob


# In[2]:
# THIS IS WHERE YOU WILL DETAIL THE NAME OF THE SHEET TO BE PROCESSED
file = input('What is the filepath that needs to be processed? ')

csv = pd.read_csv(file,encoding="ISO-8859-1")
df = pd.DataFrame(csv)
df1 = df.dropna()


# In[3]:
# return list from series of comma-separated strings
def chainer(s):
    return list(chain.from_iterable(s.str.split(',')))

# calculate lengths of splits
lens = df1['Flat RCCP'].str.split(',').map(len)


# In[4]:
# creating a new dataframe with the flat images separated out of each other

flat = pd.DataFrame({
    'Manufacturer':np.repeat(df1['Manufacturer'], lens),
    'Series':np.repeat(df1['Series'], lens),
    'Color':np.repeat(df1['Color'], lens),
    'Flat RCCP':chainer(df1['Flat RCCP'])
})


# In[5]:
flat['Flat RCCP'] = flat['Flat RCCP'] + "_FLT.dng"


# In[6]:
# calculate lengths of splits
lens2 = df1['Texture RCCP'].str.split(',').map(len)

# creating a new dataframe with the texture images separated out of each other

texture = pd.DataFrame({
    'Manufacturer':np.repeat(df1['Manufacturer'], lens2),
    'Series':np.repeat(df1['Series'], lens2),
    'Color':np.repeat(df1['Color'], lens2),
    'Texture RCCP':chainer(df1['Texture RCCP'])
})


# In[7]:
texture['Texture RCCP'] = texture['Texture RCCP'].str.replace('Use ','')


# In[8]:
texture['Texture RCCP'] = texture['Texture RCCP'] + "_TXT.dng"


# In[9]:
merged = pd.merge(flat,texture,on='Color', how='inner')


# In[10]:
merged2 = merged[['Manufacturer_x','Series_x','Color','Flat RCCP','Texture RCCP']]
clean_merge = merged2.rename(columns={'Manufacturer_x':'Manufacturer',
                       'Series_x':'Series'
                       })


# In[11]:
clean_merge.head(10)


# In[12]:
number_of_cell = len(clean_merge['Flat RCCP'])
number_of_cell2 = len(clean_merge['Texture RCCP'])


# In[13]:
mydir = input("What is the filepath with your images? ")

filelist = os.listdir(mydir)
for file in filelist[:]: # filelist[:] makes a copy of filelist
    print(file)
number_of_files = len(filelist)


# In[14]:
for i in range(number_of_cell):
        for n in range(number_of_files):
            if clean_merge['Flat RCCP'][i] == filelist[n]:
                os.rename(mydir+ filelist[n], mydir+ (clean_merge['Manufacturer'][i] + clean_merge['Series'][i] + clean_merge['Color'][i] + "FLAT" + ".dng"))
                print('Flat Image Processed Succesfully')
            elif clean_merge['Texture RCCP'][i] == filelist[n]:
                os.rename(mydir+ filelist[n], mydir+ (clean_merge['Manufacturer'][i] + clean_merge['Series'][i] + clean_merge['Color'][i] + "TEXTURE" + ".dng"))
                print('Texture Image Processed Succesfully')
            else:
                print('Could Not Process')


