import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import streamlit as st
import os
sns.set()

st.title("Linear Regression")

path = os.path.dirname(os.path.dirname(__file__))
my_file = path+'/data/sat_gpa.csv'

data = pd.read_csv(my_file)
st.write(data)

y = data ['GPA']
x1 = data ['SAT']

fig, ax = plt.subplots()
plt.scatter(x1,y, c = "blue")
plt.xlabel('SAT', fontsize = 20)
plt.ylabel('GPA', fontsize = 20)
#plt.show()
st.pyplot(plt)

x = sm.add_constant(x1)
results = sm.OLS(y,x).fit()
results.summary()

intercept = st.slider("intercept",0.1, 0.1, 0.5)

plt.scatter(x1,y)
yhat = 0.0017*x1 + intercept
plt.scatter(x1,y, c = "blue")
fig = plt.plot(x1,yhat, lw=2, label ='regression line', c= "orange" )
plt.xlabel('SAT', fontsize = 20)
plt.ylabel('GPA', fontsize = 20)
#plt.show()
st.pyplot(plt)
