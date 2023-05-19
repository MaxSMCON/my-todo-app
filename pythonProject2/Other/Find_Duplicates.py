
import pandas as pd

filepath = "Q:\Operations\Reports\Inventory Movement Analysis v4.xlsm"
df = pd.read_excel(filepath, skiprows=9)

sheet_name = 'Sheet 1'

column_name = 'Kgs'

# print(df.columns)

# Find duplicates
duplicates = df[df.duplicated(subset=column_name, keep=False)][column_name]

# Print the duplicate rows
print(duplicates[['ItemKey', 'Kgs']])
print(df[['ItemKey', 'Kgs']])