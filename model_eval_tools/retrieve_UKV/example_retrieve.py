import matplotlib.pyplot as plt

from model_eval_tools.retrieve_UKV import retrieve_ukv_vars

test_day = 2016126
test_path = 12

# BL_H
ukv_data_dict_BL_H = retrieve_ukv_vars.retrieve_UKV(test_path, test_day, test_day, variable='BL_H')
UKV_df_BL_H = retrieve_ukv_vars.UKV_df(ukv_data_dict_BL_H)
UKV_df_BL_H.plot()
plt.show()

# wind
ukv_data_dict_wind = retrieve_ukv_vars.retrieve_UKV(test_path, test_day, test_day, variable='wind')
UKV_df_wind = retrieve_ukv_vars.UKV_df(ukv_data_dict_wind, wind=True)
UKV_df_wind.wind_direction.plot()
plt.show()

# H
ukv_data_dict_QH = retrieve_ukv_vars.retrieve_UKV(test_path, test_day, test_day, variable='H')
UKV_df_QH = retrieve_ukv_vars.UKV_df(ukv_data_dict_QH)
UKV_df_QH.WAverage.plot()
plt.show()

# kdown
ukv_data_dict_kdown = retrieve_ukv_vars.retrieve_UKV(test_path, test_day, test_day, variable='kdown')
UKV_df_kdown = retrieve_ukv_vars.UKV_df(ukv_data_dict_kdown)
UKV_df_kdown.WAverage.plot()
plt.show()

print('end')