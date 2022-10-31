import pandas as pd
from pandas.util.testing import assert_frame_equal

from model_eval_tools import look_up


def create_grid_lc_csv(
        landuse_dir='C:/Users/beths/OneDrive - University of Reading/landuse/site grids/10-tile landuse (Maggie_new)/landuse_csv_files/'):
    """
    This was used to compile all the lc fractions from all grids together in one file.
    :param landuse_dir:
    :return:
    """

    # ToDo: where did the individual site csv files come from? Check this

    # Compile an overall csv file for grids 1 - 42
    list_of_grid_df = []
    for key in look_up.grid_dict_lc.keys():
        # take the first grid for this number
        grid_code = look_up.grid_dict_lc[key][0]

        # split the string to get site code and grid letter
        site = grid_code.split(' ')[0]
        letter = grid_code.split(' ')[1]

        # find the csv based on above
        file_path = landuse_dir + site + '_10T.csv'

        # read the whole csv file
        df = pd.read_csv(file_path)

        # lock on to just the row of the grid letter I want
        lc_df = df.loc[df['GRID'] == letter]

        lc_df = lc_df.drop('GRID', 1)
        lc_df.index = [key]
        lc_df.index.names = ['GRID_NUM']

        list_of_grid_df.append(lc_df)

    df = pd.concat(list_of_grid_df)
    df.to_csv(landuse_dir + 'all_grids_10T.csv')
    print('end')


def pytest_landcover_csvs(
        landuse_dir='C:/Users/beths/OneDrive - University of Reading/landuse/site grids/10-tile landuse (Maggie_new)/landuse_csv_files/'):
    """
    Test function to see if all landcover values match for expected overlapped grids between sites.
    :param landuse_dir:
    :return:
    """

    for key in look_up.grid_dict_lc.keys():

        print('GRID NUMBER: ', key)

        # define the list of grid strings (site_letter) for this grid number
        key_list = look_up.grid_dict_lc[key]

        # list to append dataframes to cor checking
        # will be including the grid col and original index
        key_vals_check = []

        for grid_code in key_list:
            print('Grid code:', grid_code)

            # split the string to get site code and grid letter
            site = grid_code.split(' ')[0]
            letter = grid_code.split(' ')[1]

            # find the csv based on above
            file_path = landuse_dir + site + '_10T.csv'

            # read the whole csv file
            df = pd.read_csv(file_path)

            # lock on to just the row of the grid letter I want
            lc_df = df.loc[df['GRID'] == letter]

            # append this 1 row df to list
            key_vals_check.append(lc_df)

        # reset the index and drop the GRID column to enable comparison
        df_to_check = []
        for df in key_vals_check:
            df = df.drop('GRID', 1)
            df = df.reset_index(drop=True)
            df_to_check.append(df)

        # make the checks to see if all df in the list equal to the first
        for df in df_to_check:
            assert_frame_equal(df, df_to_check[0])

        print('All passed')
        print(' ')


def check_KSSW_grid_stashcodes():
    """
    There is a known issue where the KSSW site can be considered to be in two grids.
    This function was made to check where data from stash codes (actual variables and not lc fractions from ancillaries)
    Match between the sites MR and KSSW, where there is overlap.

    NOTE: some of the imputs to the functions here are likely out-of-date. If this needs to be used again, will need
    to update
    :return:
    """

    from model_eval_tools.retrieve_UKV import find_model_files
    from model_eval_tools.retrieve_UKV import read_premade_model_files

    # KSSW
    file_dict_ukv_kdown_KSSW = find_model_files.find_UKV_files(2016122,
                                                               2016122,
                                                               'KSSW',
                                                               'ukv',
                                                               '21Z',
                                                               'kdown',
                                                               # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                               model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                               )

    files_ukv_kdown_KSSW = find_model_files.order_model_stashes(file_dict_ukv_kdown_KSSW, 'kdown')

    ukv_kdown_KSSW = read_premade_model_files.extract_model_data(files_ukv_kdown_KSSW,
                                                                 2016123,
                                                                 2016123,
                                                                 'kdown',
                                                                 'ukv',
                                                                 0,
                                                                 'KSSW',
                                                                 'C:/Users/beths/Desktop/LANDING/',
                                                                 grid_choice='A')

    included_models_kdown_KSSW = {}
    group_ukv_kdown_KSSW = [ukv_kdown_KSSW[5], ukv_kdown_KSSW[6], ukv_kdown_KSSW[0], ukv_kdown_KSSW[1],
                            ukv_kdown_KSSW[10]]
    included_models_kdown_KSSW['ukv'] = group_ukv_kdown_KSSW
    mod_time_kdown_KSSW, mod_vals_kdown_KSSW = read_premade_model_files.retrieve_arrays_model(
        included_models_kdown_KSSW, 'ukv')

    # MR
    file_dict_ukv_kdown_MR = find_model_files.find_UKV_files(2016122,
                                                             2016122,
                                                             'MR',
                                                             'ukv',
                                                             '21Z',
                                                             'kdown',
                                                             # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                             model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                             )
    files_ukv_kdown_MR = find_model_files.order_model_stashes(file_dict_ukv_kdown_MR, 'kdown')

    ukv_kdown_MR = read_premade_model_files.extract_model_data(files_ukv_kdown_MR,
                                                               2016123,
                                                               2016123,
                                                               'kdown',
                                                               'ukv',
                                                               0,
                                                               'MR',
                                                               'C:/Users/beths/Desktop/LANDING/',
                                                               grid_choice='E')

    included_models_kdown_MR = {}
    group_ukv_kdown_MR = [ukv_kdown_MR[5], ukv_kdown_MR[6], ukv_kdown_MR[0], ukv_kdown_MR[1], ukv_kdown_MR[10]]
    included_models_kdown_MR['ukv'] = group_ukv_kdown_MR
    mod_time_kdown_MR, mod_vals_kdown_MR = read_premade_model_files.retrieve_arrays_model(included_models_kdown_MR,
                                                                                          'ukv')

    print('end')
