import re
import pandas as pd

path = ''
_property = re.search(r'content\/(.*)\_\d+', path)[1]
excluded_floor = [4, 13, 14, 24, 34, 44, 54, 64]

df = pd.read_excel(path)
cols = ['Tower Index', 'Tower', 'Floor']
df.loc[:, cols] = df.loc[:, cols].ffill()

df2 = df.loc[:1].copy()
# df3 = df.loc[55:65].copy()
# df4 = df.loc[99:104].copy()
# df5 = df.loc[136:145].copy()
# df6 = df.loc[31:33].copy()
# df7 = df.loc[40:41].copy()
# df8 = df.loc[44:49].copy()
# df9 = df.loc[50:53].copy()
# df10 = df.loc[70:73].copy()
# df11 = df.loc[74:77].copy()
# df12 = df.loc[84:85].copy()

df13 = df2.copy()
df13['Floor'] = 3
for i in range(5, 27):
  if i not in excluded_floor:
    df14 = df2.copy()
    df14['Floor'] = i
    df13 = pd.concat([df13, df14])

# df14 = df3.copy()
# df14['Floor'] = 5
# for i in range(6, 37):
#   if i not in excluded_floor:
#     df15 = df3.copy()
#     df15['Floor'] = i
#     df14 = pd.concat([df14, df15])

# df15 = df4.copy()
# df15['Floor'] = 6
# for i in range(7, 38):
#   if i not in excluded_floor:
#     df16 = df4.copy()
#     df16['Floor'] = i
#     df15 = pd.concat([df15, df16])

# df16 = df5.copy()
# df16['Floor'] = 6
# for i in range(7, 39):
#   if i not in excluded_floor:
#     df17 = df5.copy()
#     df17['Floor'] = i
#     df16 = pd.concat([df16, df17])

# df17 = df6.copy()
# df17['Floor'] = 19
# for i in range(20, 25):
#   if i not in excluded_floor:
#     df18 = df6.copy()
#     df18['Floor'] = i
#     df17 = pd.concat([df17, df18])

# df18 = df7.copy()
# df18['Floor'] = 7
# for i in range(8, 10):
#   if i not in excluded_floor:
#     df19 = df7.copy()
#     df19['Floor'] = i
#     df18 = pd.concat([df18, df19])

# df19 = df8.copy()
# df19['Floor'] = 12
# for i in range(13, 17):
#   if i not in excluded_floor:
#     df20 = df8.copy()
#     df20['Floor'] = i
#     df19 = pd.concat([df19, df20])

# df20 = df9.copy()
# df20['Floor'] = 18
# for i in range(19, 25):
#   if i not in excluded_floor:
#     df21 = df9.copy()
#     df21['Floor'] = i
#     df20 = pd.concat([df20, df21])

# df21 = df10.copy()
# df21['Floor'] = 11
# for i in range(12, 25):
#   if i not in excluded_floor:
#     df22 = df10.copy()
#     df22['Floor'] = i
#     df21 = pd.concat([df21, df22])

# df22 = df11.copy()
# df22['Floor'] = 26
# for i in range(12, 25):
#   if i not in excluded_floor:
#     df23 = df11.copy()
#     df23['Floor'] = i
#     df22 = pd.concat([df22, df23])

# df23 = df12.copy()
# df23['Floor'] = 11
# for i in range(12, 25):
#   if i not in excluded_floor:
#     df24 = df12.copy()
#     df24['Floor'] = i
#     df23 = pd.concat([df23, df24])

df = pd.concat([df, df13])
df['Property'] = _property
df = df.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
print(len(df))

print(df['SFA'].unique()[:2])
print(df['FR'].unique()[:2])
print(df['Roof'].unique()[:2])
print(df['Garden'].unique()[:2])
print(df['Stairhood'].unique()[:2])
print(df['Bay Window'].unique()[:2])
print(df['Parking Space'].unique()[:2])

df[['SFA', 'Bal']] = df['SFA'].str.split(' Balcony             露台        ：', expand=True)
df[['Bal', 'UP']] = df['Bal'].str.split(' Utility Platform   工作平台    ：', expand=True)
df[['UP', 'Verandah']] = df['UP'].str.split(' Verandah           陽台        ：', expand=True)
# df['Verandah'] = '-'

df[['SFA (sq. m.)', 'SFA']] = df['SFA'].str.split('(', expand=True)
df['SFA'] = df['SFA'].apply(lambda x: x[:-1].strip())

df['Bal'] = df['Bal'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Bal (sq. m.)', 'Bal']] = df['Bal'].str.split('(', expand=True)
df['Bal'] = df['Bal'].apply(lambda x: x[:-1].strip())

df['UP'] = df['UP'].apply(lambda x: '- (-)' if x == '-' else x)
df[['UP (sq. m.)', 'UP']] = df['UP'].str.split('(', expand=True)
df['UP'] = df['UP'].apply(lambda x: x[:-1].strip())

df['Verandah'] = df['Verandah'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Verandah (sq. m.)', 'Verandah']] = df['Verandah'].str.split('(', expand=True)
df['Verandah'] = df['Verandah'].apply(lambda x: x[:-1].strip())

df['FR'] = df['FR'].apply(lambda x: '- (-)' if x == '-' else x)
df[['FR (sq. m.)', 'FR']] = df['FR'].str.split('(', expand=True)
df['FR'] = df['FR'].apply(lambda x: x[:-1].strip())

df['Roof'] = df['Roof'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Roof (sq. m.)', 'Roof']] = df['Roof'].str.split('(', expand=True)
df['Roof'] = df['Roof'].apply(lambda x: x[:-1].strip())

df['Air-Conditioning Plant Room'] = df['Air-Conditioning Plant Room'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Air-Conditioning Plant Room (sq. m.)', 'Air-Conditioning Plant Room']] = df['Air-Conditioning Plant Room'].str.split('(', expand=True)
df['Air-Conditioning Plant Room'] = df['Air-Conditioning Plant Room'].apply(lambda x: x[:-1].strip())

df['Bay Window'] = df['Bay Window'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Bay Window (sq. m.)', 'Bay Window']] = df['Bay Window'].str.split('(', expand=True)
df['Bay Window'] = df['Bay Window'].apply(lambda x: x[:-1].strip())

df['Cockloft'] = df['Cockloft'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Cockloft (sq. m.)', 'Cockloft']] = df['Cockloft'].str.split('(', expand=True)
df['Cockloft'] = df['Cockloft'].apply(lambda x: x[:-1].strip())

df['Garden'] = df['Garden'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Garden (sq. m.)', 'Garden']] = df['Garden'].str.split('(', expand=True)
df['Garden'] = df['Garden'].apply(lambda x: x[:-1].strip())

df['Parking Space'] = df['Parking Space'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Parking Space (sq. m.)', 'Parking Space']] = df['Parking Space'].str.split('(', expand=True)
df['Parking Space'] = df['Parking Space'].apply(lambda x: x[:-1].strip())

df['Stairhood'] = df['Stairhood'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Stairhood (sq. m.)', 'Stairhood']] = df['Stairhood'].str.split('(', expand=True)
df['Stairhood'] = df['Stairhood'].apply(lambda x: x[:-1].strip())

df['Terrace'] = df['Terrace'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Terrace (sq. m.)', 'Terrace']] = df['Terrace'].str.split('(', expand=True)
df['Terrace'] = df['Terrace'].apply(lambda x: x[:-1].strip())

df['Yard'] = df['Yard'].apply(lambda x: '- (-)' if x == '-' else x)
df[['Yard (sq. m.)', 'Yard']] = df['Yard'].str.split('(', expand=True)
df['Yard'] = df['Yard'].apply(lambda x: x[:-1].strip())

cols = [
    'Tower Index', 'Property', 'Tower', 'Floor', 'Unit', 'SFA', 'SFA (sq. m.)', 'Bal', 'Bal (sq. m.)', 'UP', 'UP (sq. m.)',
    'Verandah', 'Verandah (sq. m.)', 'FR', 'FR (sq. m.)', 'Roof', 'Roof (sq. m.)', 'Air-Conditioning Plant Room',
    'Air-Conditioning Plant Room (sq. m.)', 'Bay Window', 'Bay Window (sq. m.)', 'Cockloft', 'Cockloft (sq. m.)',
    'Garden', 'Garden (sq. m.)', 'Parking Space', 'Parking Space (sq. m.)', 'Stairhood', 'Stairhood (sq. m.)',
    'Terrace', 'Terrace (sq. m.)', 'Yard', 'Yard (sq. m.)', 'Flat Mix', 'BR', 'E', 'T', 'OK', 'M', 'S', 'WIC',
    'Orientation1', 'Orientation2', 'View1', 'View2'
]
df = df[cols]
df.sort_values(['Tower Index', 'Unit', 'Floor'], ascending=[True, True, False], inplace=True)
df.drop(['Tower Index'], axis=1, inplace=True)
df.reset_index(drop=True, inplace=True)

parts = path.split('/')[-1].split('.')[0].split('_')
property_name = '_'.join([x.lower() for x in parts[0].split(' ')])
date_code = parts[1]

df.to_csv(f'{property_name}_units_{date_code}.csv', index=False)
