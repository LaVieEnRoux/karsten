import sys
from loadValidation import loadValidation
from valTable import valTable
import pandas as pd

path = 'val_struct.pkl'

# create validation struct, and make .csv files from it
loadValidation()
valTable(path)

# load in .csv file as command line arg and print it out
csv_file = 'valTables/{}_val.csv'.format(sys.argv[1])
table = pd.DataFrame.from_csv(csv_file)
print table
