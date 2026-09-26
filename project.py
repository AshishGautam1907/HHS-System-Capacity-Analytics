import pandas as pd
import numpy as np

df= pd.read_csv('HHS_Unaccompanied_Alien_Children_Program.csv')

# print(df.head(10))
# missing value 
print("missing value in each column:")
print(df.isnull().sum())
# remove misssing raws
df=df.dropna(how="all")
# print(df.isnull().sum())
# for verifying the data type of each column
pd.set_option("display.max_columns",None)
pd.set_option("display.width",None)
print(df.shape)
print(df.head())
print(df.tail())
df=df.drop_duplicates()
print(df.isnull().sum())
