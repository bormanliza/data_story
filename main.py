import pandas as pd

data_welzijn_path = 'gezondheid_in_beeld.csv'
data_park_path = 'PARKPLANTSOENGROEN.csv'

data_welzijn = pd.read_csv(data_welzijn_path, delimiter=';')
data_park = pd.read_csv(data_park_path, delimiter=';')

# columns = data_welzijn.columns.tolist()

# columns_str = ''.join(columns)

# print(rows * columns)
# print(len(columns_str.split(';')))
# print(data_welzijn.head())

# health_good_very_good = data_welzijn['ZwareDrinker_14']

# health_good_very_good = pd.to_numeric(health_good_very_good, errors='coerce')

# description = health_good_very_good.describe()

rows_welzijn, cols_welzijn = data_welzijn.shape
points_welzijn = rows_welzijn * cols_welzijn # 828549

rows_park, cols_park = data_park.shape
points_park = rows_park * cols_park # 1116

print(cols_park)

stadspark = data_park['Stadspark']
description_stadspark = stadspark.describe()

oppervlakte = data_park['Oppervlakte_m2']
oppervlakte = pd.to_numeric(oppervlakte, errors='coerce')
description_oppervlakte = oppervlakte.describe()
