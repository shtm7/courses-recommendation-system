# import arabic_reshaper
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


df= pd.read_csv('./data/Academy Full Pack clean.csv' , encoding = "UTF-8")


rate=pd.read_csv('./data/rate clean.csv' , encoding = "UTF-8")


intrest=pd.read_csv('./data/intrest clean.csv' , encoding = "UTF-8")
#############################################

data=pd.merge(df,intrest,on='student_id')
intr=data[['student_id', 'course_id', 'course_name']]

#######################################
from sklearn.preprocessing import LabelEncoder
encoder= LabelEncoder()
data['intr_no']=encoder.fit_transform(data['intrest'].fillna(np.nan))

# data.to_csv('./data/data.csv')

# convert the word catagorical lables to numbers 

from sklearn.preprocessing import LabelEncoder
import numpy as np

def encoder(df,col):
    encoder= LabelEncoder()
    df[col]=encoder.fit_transform(df[col].fillna(np.nan))
    return df[col]
encoder(data , 'intrest')
print('')
