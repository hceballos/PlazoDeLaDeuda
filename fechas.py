import numpy as np
import pandas as pd


df = pd.DataFrame(columns=["one", "two"])


#df.one = ["2019-01-24"]
df.one = pd.to_datetime(["2019-01-24"])

#df.two = ["2019-01-28"]
df.two = pd.to_datetime(["2019-01-28"])

print(df)

difference = (df.two - df.one)

print(difference)