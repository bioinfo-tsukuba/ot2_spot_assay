import pandas as pd
import sys

OD600 = pd.read_csv(sys.argv[1]) 
num_samples = sys.argv[2]

OD600_melt = pd.melt(OD600, id_vars='Unnamed: 0', var_name='col_num', value_name='absorbance')
OD600_melt_int= OD600_melt.assign(int_col_num=OD600_melt['col_num'].astype(int)).dropna(how='any')
OD600_melt_int_sort=OD600_melt_int.sort_values(['Unnamed: 0', 'int_col_num']).reset_index(drop=False)

dict_dispense={}
for i in range(int(num_samples)):
    dispense = (0.02 / (OD600_melt_int_sort.absorbance[i] - 0.030)) * 200
    dict_dispense[i]=[int(dispense)]

df_dispense = pd.DataFrame(data=dict_dispense)

df_dispense.to_csv(sys.argv[3])