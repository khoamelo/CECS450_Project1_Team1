import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

df = pd.read_csv('StressLevelDataset.csv')
print(df)