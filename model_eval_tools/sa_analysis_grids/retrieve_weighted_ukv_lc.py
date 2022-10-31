import pandas as pd
import numpy as np
import os


def weight_lc_fractions(model_site_dict, percentage_vals_dict, DOYstart,
                        lc_csv='C:/Users/beths/OneDrive - University of Reading/landuse/site grids/10-tile landuse (Maggie_new)/landuse_csv_files/all_grids_10T.csv'):
    """
    Function which takes the UKV landcover fractions for each gridbox in the observation SA at given timestep,
    and weights the fractions accroding to SA weighting in that grid.
    :return:
    """

    # ToDo: move the csv file in input to this location

    assert model_site_dict.keys() == percentage_vals_dict.keys()

    # read in csv df
    lc_df = pd.read_csv(lc_csv)

    weighted_lc_dfs = []

    for hour in model_site_dict.keys():

        grid_numbers = model_site_dict[hour]
        grid_weights = percentage_vals_dict[hour]

        grid_lc_df_list_unweighted = []
        grid_lc_df_list_weighted = []

        for grid, weight in zip(grid_numbers, grid_weights):
            grid = int(grid)
            # find the grid in the lc df
            target_lc_df = lc_df.loc[lc_df['GRID_NUM'] == grid]
            target_lc_df = target_lc_df.set_index('GRID_NUM')

            grid_lc_df_list_unweighted.append(target_lc_df)

            # apply weighting
            weight = weight / 100

            weighted_df = target_lc_df * weight

            grid_lc_df_list_weighted.append(weighted_df)

        combine_weighted_df = pd.concat(grid_lc_df_list_weighted)

        combine_weighted_df.loc['W_SUM'] = combine_weighted_df.sum(numeric_only=True, axis=0)
        assert np.isclose(combine_weighted_df.loc['W_SUM'].sum(), 1)

        for i in combine_weighted_df.index:
            if type(i) != str:
                combine_weighted_df.drop(i, inplace=True)

        combine_weighted_df.index = [hour]
        weighted_lc_dfs.append(combine_weighted_df)

    df = pd.concat(weighted_lc_dfs)

    # get current directory
    csv_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\',
                                                                  '/') + '/../sa_analysis_grids/ukv_grid_sa_percentages.csv'


    df.to_csv('C:/Users/beths/Desktop/LANDING/weighted_lc_ukv_' + str(DOYstart) + '.csv')

    return df
