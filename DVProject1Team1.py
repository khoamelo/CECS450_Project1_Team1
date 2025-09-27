import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

df = pd.read_csv('StressLevelDataset.csv')

fig = px.scatter_matrix(df, 
                            dimensions=["anxiety_level", "self_esteem", "depression", "sleep_quality"],
                            color="stress_level",
                            height=800,
                            width=800,
                            title="Scatter matrix of stress level vs. several related factors"
                        )

fig.write_html("scatter_matrix.html")
#print(df)