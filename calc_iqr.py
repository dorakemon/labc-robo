# https://qiita.com/papi_tokei/items/6f77a2a250752cfa850b
import pandas as pd
a = [0 , 50, 55, 50, 47, 100, 54, 57, 90, 10]
apd = pd.Series(a)
Q1 = apd.quantile(0.25)
Q3 = apd.quantile(0.75)
IQR = Q3 - Q1
LOWER_Q = Q1 - 1.5 * IQR
HIGHER_Q = Q3 + 1.5 * IQR

apd_iqr = apd[(LOWER_Q <= apd) & (apd <= HIGHER_Q)].dropna()
print(apd_iqr)