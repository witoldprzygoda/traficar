import pandas as pd
df = pd.read_csv('data/consumption.csv')
print(f"Total consumption: {df['consumption_percentage'].sum():.2f}%")
print(f"Average per 10min: {df['consumption_percentage'].mean():.2f}%")
