import pandas as pd
from openpyxl import load_workbook

# Load the existing Excel file
file_path = '..//data/parameter_list.xlsx'
df = pd.read_excel(file_path)

# Modify specific columns for existing rows
df.loc[df['Name'] == 'Alice', 'Score'] = 95  # Updating Alice's Score
df.loc[df['Name'] == 'Bob', ['Age', 'Score']] = [32, 87]  # Updating Bob's Age and Score

# Write back the modified DataFrame
with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
    df.to_excel(writer, index=False)
