#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import pandas as pd
import numpy as np
import os
import csv
from itertools import chain
import shutil


# In[ ]:
# This code reads in your file, creates a dataframe, and removes all rows with missing data
# IMPORTANT - ensure your csv file does not have any unneccesary blank rows, as this will
# cause the data to be deleted
file = input('What is the filepath that needs to be processed? ')
csv = pd.read_csv(file,encoding="ISO-8859-1")
df = pd.DataFrame(csv)
df1 = df.dropna()


# In[ ]:
# return list from series of comma-separated strings
# found this bit of code online, essentially what this will do is create a list of strings
# from a given iterable - i.e. array, list, etc. and will split it on the character ","
# so when a product has more than one image number for an RCCP, it will be split into
# individual columns

def chainer(s):
    return list(chain.from_iterable(s.str.split(', ')))
# calculate lengths of splits
lens = df1['Flat RCCP'].str.split(', ').map(len)
lens2 = df1['Texture RCCP'].str.split(', ').map(len)

df1['Flat RCCP'] = df1['Flat RCCP'].str.replace(",",", ")
df1['Texture RCCP'] = df1['Texture RCCP'].str.replace(",",", ")


# In[ ]:
# creating two new dataframes that contain rows of each split that was made above
# for example, if a product had the flat rccp value '234,235' - the below dataframe
# would now have two rows for that product, one for each number in the flat rccp value
#
# The same is done for the texture rccp values
#
# With the two dataframes created, I merge them together to generate our final cleaned dataframe
# which we will generate all of our new image names from
flat = pd.DataFrame({
    'Manufacturer':np.repeat(df1['Manufacturer'], lens),
    'Series':np.repeat(df1['Series'], lens),
    'Color':np.repeat(df1['Color'], lens),
    'Flat RCCP':chainer(df1['Flat RCCP'])
})
text = pd.DataFrame({
    'Manufacturer':np.repeat(df1['Manufacturer'], lens2),
    'Series':np.repeat(df1['Series'], lens2),
    'Color':np.repeat(df1['Color'],lens2),
    'Texture RCCP':chainer(df1['Texture RCCP'])
})
merge_df = pd.merge(flat,text)

# This chunk of code is bulky, but will be used to ensure that there are no errors in the naming of any of the files
merge_df['Manufacturer'] = merge_df['Manufacturer'].str.replace('/','-').replace("*",'-').replace('&','-').replace('%','-').replace('!','-').replace("'","")
merge_df['Series'] = merge_df['Series'].str.replace('/','-').replace("*",'-').replace('&','-').replace('%','-').replace('!','-').replace("'","")
merge_df['Color'] = merge_df['Color'].str.replace('/','-').replace("*",'-').replace('&','-').replace('%','-').replace('!','-').replace("'","")

# In[ ]:
# This block of code is used to iterate through the data Series, and clean it to be ingested
# for use with the images. Here we are ensuring that Flat and Texture RCCP row values will
# match up with the image names in our folders
merge_df['Flat RCCP'] = merge_df['Flat RCCP'].str.strip() + "_FLT.dng"
merge_df['Texture RCCP'] = merge_df['Texture RCCP'].str.strip().str.replace('Use ','')
merge_df['Texture RCCP'] = merge_df['Texture RCCP'] + "_TXT.dng"


# In[ ]:
# I created this range so that I could iterate through the items below
number_of_cell = len(merge_df['Color'])
merge_df['product_key'] = merge_df['Series'].str.strip() + merge_df['Color'].str.strip()
merge_df['Text_Name'] = merge_df['Manufacturer'].str.strip() + "_" + merge_df['Series'].str.strip()

# In[ ]:
# this block of code is specifically used to handle products who have more than one
# photo for their respective RCCP. Essentially, if one product has two ids - we want to
# add a unique signifier for the duplicate so that we do not get errors in a file name
#
# for example - if 'Cool Breeze' has two flat rccps, you can expect there to be two rows with
# the color value 'Cool Breeze' - as seen in [cell 4] - but that will be problem when it comes
# time to rename the files - if the file name corresponding to 'Cool Breeze' has already been made
# the code will break when it trys to rename the second instance of 'Cool Breeze' as the first
# already exists.
#
# This block walks through the color series and checks if any adjacent values are duplicates, if so
# please append 'Part1' to the original and 'Part2' to the duplicate

for i in range(number_of_cell - 1):
    try:
        if merge_df['product_key'][i] == merge_df['product_key'][i+1]:
            merge_df['Color'][i] = merge_df['Color'][i].strip() + "_Part1"
            merge_df['Color'][i+1] = merge_df['Color'][i+1].strip() + "_Part2"
        elif merge_df['product_key'][i] == merge_df['product_key'][i+2]:
            merge_df['Color'][i] = merge_df['Color'][i].strip() + "_Part1"
            merge_df['Color'][i+1] = merge_df['Color'][i+1].strip() + "_Part2"
            merge_df['Color'][i+2] = merge_df['Color'][i+2].strip() + "_Part3"
        elif merge_df['product_key'][i] == merge_df['product_key'][i+3]:
            merge_df['Color'][i] = merge_df['Color'][i].strip() + "_Part1"
            merge_df['Color'][i+1] = merge_df['Color'][i+1].strip() + "_Part2"
            merge_df['Color'][i+2] = merge_df['Color'][i+2].strip() + "_Part3"
            merge_df['Color'][i+3] = merge_df['Color'][i+3].strip() + "_Part4"
    except:
         print('This number is out of range')

merge_df['Flat_Name'] = merge_df['Manufacturer'].str.strip() + "_" + merge_df['Series'].str.strip() + merge_df['Color'].str.strip()

for i in range(number_of_cell - 1):
    if merge_df['Texture RCCP'][i] != merge_df['Texture RCCP'][i+1]:
        merge_df['Text_Name'][i] = merge_df['Text_Name'][i].strip() + "_" + merge_df['Color'][i].strip()

for i in range(number_of_cell - 1):  
    if merge_df['Flat RCCP'][i] == merge_df['Flat RCCP'][i+1]:
        merge_df['Flat_Name'][i] = merge_df['Flat_Name'][i].replace('_Part1','')

# In[ ]:
# this line simply exports the new dataframe to a csv file
# I used this in order to inspect my data when given confusing or blank errors
merge_df.to_csv(input('What would you like to name your data file? '))


# In[ ]:
# This block imports the desired image folder/directory, and prints the folders contents to the terminal
# Additionally, the last line creates a range of the number of files in the directory that I will use to iterate
# through when renaming the images
mydir = input("What is the filepath with your images? ")
filelist = os.listdir(mydir)
for file in filelist[:]: # filelist[:] makes a copy of filelist
    print(file)
number_of_files = len(filelist)

copiedDir = input("Please enter a directory path to store your source images: ")
os.mkdir(copiedDir)


# In[ ]:
# IMPORTANT NOTE - all fields must not have the characters "/", "\", or "*" [NOTE - I'm sure there are more, just haven't found them yet] as it will disrupt the code written below
# This is a complex piece of code that I 'frankensteined' together from research online.
#
# Essentially, it does the following:
#
# Looks two ranges - the number of values in the color column (I did this is all columns will have the same number of rows - it didn't really matter that I chose color)
# and the number of files in the file directory that was referenced.
#
# Next, I generate the new file names for both the flat and the texture images - I use the root folder (mydir) plus a series of dataframe values to rename the image
# These values are the Manufacturer name, series, and color - with the added _FLAT or _TEXTURE suffix depending upon the use, and the .dng to maintain the file
# format
#
# Now I loop through the code - I do a check to see if the name of a given file - matches either the Flat RCCP or Texture RCCP value in the dataframe
# if they match, then I use the os.rename function to rename the old file to the new file names I generated above
# if they don't, I have it print out a statement saying that no match was found
for i in range(number_of_cell):
        for n in range(number_of_files):
            new_flat_file = mydir + (merge_df['Flat_Name'][i].strip() + "_FLAT" + ".dng")
            new_text_file = mydir + (merge_df['Text_Name'][i].strip() + "_TEXTURE" + ".dng")
            if  filelist[n] == merge_df['Flat RCCP'][i]:
                try:
                    shutil.copy(mydir + filelist[n], copiedDir)
                    os.rename(mydir + filelist[n], new_flat_file)
                    print(f"flat image {new_flat_file} processed") 
                except:
                    print('Flat Image Id NOT FOUND - or - Option has TWO pieces')
            elif  filelist[n] == merge_df['Texture RCCP'][i]:
                try:
                    shutil.copy(mydir + filelist[n], copiedDir)
                    os.rename(mydir + filelist[n], new_text_file)
                    print(f"texture image {new_text_file} processed")
                except:
                    print('Texture Image Id NOT FOUND - or - Option has TWO pieces')