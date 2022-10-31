import datetime as dt
import pandas as pd
import os

from model_eval_tools.retrieve_UKV import retrieve_ukv_vars_tools
from model_eval_tools.sa_analysis_grids import ukv_values_from_SA_analysis
from model_eval_tools.retrieve_UKV import read_premade_model_files
from model_eval_tools.retrieve_UKV import find_model_files


def retrieve_UKV(scint_path,
                 DOYstart,
                 DOYstop,
                 variable='H',
                 run='21Z',
                 sa_analysis=True,
                 av_disheight=False):
    """
    """

    setup_run_dict = retrieve_ukv_vars_tools.UKV_setup_run(scint_path, variable, DOYstart, DOYstop)
    site = setup_run_dict['site']
    savepath = setup_run_dict['save_folder']

    return_model_DOY_dict = retrieve_ukv_vars_tools.UKV_return_model_DOY(DOYstart, DOYstop, run)
    DOYstart_mod = return_model_DOY_dict['DOYstart_mod']
    DOYstop_mod = return_model_DOY_dict['DOYstop_mod']

    model_grid_vals = {}
    model_grid_time = {}

    if variable == 'H' or variable == 'kdown':

        if sa_analysis == True:

            in_dir_sa_list = 'C:/Users/beths/Desktop/LANDING/fp_output/' + str(DOYstart)[4:] + '/hourly/'

            time = retrieve_ukv_vars_tools.retrieve_SA_hours(in_dir_sa_list, DOYstart)

            # find source area raster
            sa_list = retrieve_ukv_vars_tools.find_source_area(time=time,
                                                               in_dir=in_dir_sa_list)


            # get current directory
            cwd = os.getcwd()
            csv_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/../sa_analysis_grids/ukv_grid_sa_percentages.csv'

            model_site_dict, percentage_vals_dict, percentage_covered_by_model = ukv_values_from_SA_analysis.prepare_model_grid_percentages(
                time=time,
                sa_list=sa_list,
                savepath=savepath,
                csv_path=csv_dir)

            # ToDo: hardcoding disheight here as 0. This is ok for now - as it's a surface stash code
            included_grids, model_site = ukv_values_from_SA_analysis.determine_which_model_files(model_site_dict,
                                                                                                 DOYstart_mod,
                                                                                                 DOYstop_mod,
                                                                                                 run,
                                                                                                 variable,
                                                                                                 0,
                                                                                                 savepath)

            included_grids = ukv_values_from_SA_analysis.average_model_grids(included_grids,
                                                                             DOYstart_mod,
                                                                             DOYstop_mod,
                                                                             percentage_vals_dict,
                                                                             model_site_dict,
                                                                             model_site)

            for grid_choice in included_grids.keys():
                mod_time, mod_vals = read_premade_model_files.retrieve_arrays_model(included_grids, grid_choice)

                model_grid_vals[grid_choice] = mod_vals

                if variable == 'kdown':
                    # push kdown vals forward by 15 mins - as model output is 15 min average time starting
                    model_grid_time[grid_choice] = mod_time + dt.timedelta(minutes=15)

                else:
                    model_grid_time[grid_choice] = mod_time

        else:

            model_site_dict = False

            file_dict_ukv_13 = find_model_files.find_UKV_files(DOYstart_mod,
                                                               DOYstop_mod,
                                                               site,
                                                               'ukv',
                                                               run,
                                                               variable,
                                                               model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                               # model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                               )

            files_ukv_13 = find_model_files.order_model_stashes(file_dict_ukv_13, variable)

            # height still hardcoded 0 as it's a surface stash code
            ukv_13 = read_premade_model_files.extract_model_data(files_ukv_13,
                                                                 DOYstart_mod,
                                                                 DOYstop_mod,
                                                                 variable,
                                                                 'ukv',
                                                                 0,
                                                                 site,
                                                                 savepath,
                                                                 grid_choice='E')

            H_13_list = [ukv_13[5], ukv_13[6], ukv_13[0], ukv_13[1], ukv_13[10]]
            included_H = {'13': H_13_list}

            mod_time_13, mod_vals_13 = read_premade_model_files.retrieve_arrays_model(included_H, '13')
            model_grid_vals['13'] = mod_vals_13

            if variable == 'kdown':
                # push kdown vals forward by 15 mins - as model output is 15 min average time starting
                model_grid_time['13'] = mod_time_13 + dt.timedelta(minutes=15)

            else:
                model_grid_time['13'] = mod_time_13

    if variable == 'H' or variable == 'BL_H':

        # PLOT BL STASH CODE
        file_dict_ukv_BL_H_13 = find_model_files.find_UKV_files(DOYstart_mod,
                                                                DOYstop_mod,
                                                                site,
                                                                'ukv',
                                                                run,
                                                                'BL_H',
                                                                model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                                # model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                                )

        files_ukv_BL_H_13 = find_model_files.order_model_stashes(file_dict_ukv_BL_H_13, 'BL_H')

        # from scint_eval.functions import stats_of_BL_H
        # stats_of_BL_H.stats_BL_flux(files_ukv_13)

        # ToDo: hardcoding disheight here as 70. This isn't the best - this needs to be able to change
        ukv_BL_H_13 = read_premade_model_files.extract_model_data(files_ukv_BL_H_13,
                                                                  DOYstart_mod,
                                                                  DOYstop_mod,
                                                                  'BL_H',
                                                                  'ukv',
                                                                  70,
                                                                  site,
                                                                  savepath,
                                                                  grid_choice='E')

        BL_H_13_list = [ukv_BL_H_13[5], ukv_BL_H_13[6], ukv_BL_H_13[0], ukv_BL_H_13[1], ukv_BL_H_13[10]]
        included_BL_H = {'BL_H_13': BL_H_13_list}
        mod_time_13, mod_vals_13 = read_premade_model_files.retrieve_arrays_model(included_BL_H, 'BL_H_13')
        model_grid_vals['BL_H_13'] = mod_vals_13
        model_grid_time['BL_H_13'] = mod_time_13

        BL_H_z = ukv_BL_H_13[10]

        if variable == 'BL_H':
            model_site_dict = False

    else:
        BL_H_z = False

    if variable == 'kdown':

        if sa_analysis == True:
            # kdown from all grids

            # get current directory
            cwd = os.getcwd()
            csv_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/../sa_analysis_grids/ukv_grid_sa_percentages_all_grids.csv'

            model_site_dict_all, percentage_vals_dict_all, percentage_covered_by_model_all = ukv_values_from_SA_analysis.prepare_model_grid_percentages(
                time=time,
                sa_list=sa_list,
                savepath=savepath,
                csv_path=csv_dir)

            included_grids_kdown_all, model_site_kdown_all = ukv_values_from_SA_analysis.determine_which_model_files(
                model_site_dict_all,
                DOYstart_mod,
                DOYstop_mod,
                run,
                variable,
                0,
                savepath)

            included_grids_kdown_all = ukv_values_from_SA_analysis.average_model_grids(included_grids_kdown_all,
                                                                                       DOYstart_mod,
                                                                                       DOYstop_mod,
                                                                                       percentage_vals_dict_all,
                                                                                       model_site_dict_all,
                                                                                       model_site_kdown_all)

            model_grid_vals_kdown_all = {}
            model_grid_time_kdown_all = {}

            for grid_choice in included_grids_kdown_all.keys():
                mod_time, mod_vals = read_premade_model_files.retrieve_arrays_model(included_grids_kdown_all,
                                                                                    grid_choice)

                model_grid_vals_kdown_all[grid_choice] = mod_vals

                # push kdown vals forward by 15 mins - as model output is 15 min average time starting
                model_grid_time_kdown_all[grid_choice] = mod_time + dt.timedelta(minutes=15)

            all_grids_kdown_dict = {'model_grid_time_kdown_all': model_grid_time_kdown_all,
                                    'model_grid_vals_kdown_all': model_grid_vals_kdown_all,
                                    'model_site_dict_all': model_site_dict_all}

        else:
            all_grids_kdown_dict = False

    else:
        all_grids_kdown_dict = False

    if variable == 'wind':
        # finding UKV files
        file_dict_ukv_wind = find_model_files.find_UKV_files(DOYstart_mod,
                                                             DOYstop_mod,
                                                             'IMU',
                                                             'ukv',
                                                             run,
                                                             'wind',
                                                             model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                             # model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                             )

        files_ukv_wind = find_model_files.order_model_stashes(file_dict_ukv_wind, 'wind')

        ukv_wind = read_premade_model_files.extract_model_data_wind(files_ukv_wind,
                                                                    DOYstart,
                                                                    DOYstop,
                                                                    'wind',
                                                                    'ukv',
                                                                    av_disheight,
                                                                    'BCT',
                                                                    savepath,
                                                                    grid_choice='E')

        # define dict for included models
        included_models_ws = {}
        # stringtimelon, stringwindlon, lontimedict, lonwinddict, modheightvaluelon
        group_ukv_ws = [ukv_wind[3], ukv_wind[4], ukv_wind[0], ukv_wind[1], ukv_wind[6]]

        included_models_wd = {}
        # stringtimelon, stringdirlon, lontimedict, londirdict, modheightvaluelon
        group_ukv_wd = [ukv_wind[3], ukv_wind[5], ukv_wind[0], ukv_wind[2], ukv_wind[6]]

        # append to dict
        included_models_ws['ukv'] = group_ukv_ws
        included_models_wd['ukv'] = group_ukv_wd

        mod_time_ws, mod_vals_ws = read_premade_model_files.retrieve_arrays_model(included_models_ws, 'ukv')
        mod_time_wd, mod_vals_wd = read_premade_model_files.retrieve_arrays_model(included_models_wd, 'ukv')

        assert mod_time_ws.all() == mod_time_wd.all()

        model_grid_time['wind'] = mod_time_ws
        model_grid_vals['wind_speed'] = mod_vals_ws
        model_grid_vals['wind_direction'] = mod_vals_wd

        model_site_dict = False

        BL_H_z = ukv_wind[6]

    return {'model_grid_time': model_grid_time, 'model_grid_vals': model_grid_vals, 'model_site_dict': model_site_dict,
            'BL_H_z': BL_H_z, 'savepath': savepath, 'all_grids_kdown_dict': all_grids_kdown_dict}


def UKV_df(ukv_data_dict,
           time_key='model_grid_time',
           val_key='model_grid_vals',
           wind=False):
    """
    Function to convert retrieve UKV vars into coherent df
    :param ukv_data_dict:
    :param time_key:
    :param val_key:
    :param wind:
    :return:
    """

    # time
    UKV_time = ukv_data_dict[time_key]
    UKV_vals = ukv_data_dict[val_key]

    if not wind:
        assert UKV_time.keys() == UKV_vals.keys()

        list_of_UKV_df = []
        for key in UKV_time.keys():
            vals = UKV_vals[key]
            times = UKV_time[key]

            df = pd.DataFrame.from_dict({'time': times, key: vals})
            df = df.set_index('time')
            list_of_UKV_df.append(df)

    else:
        list_of_UKV_df = []
        for key in UKV_time.keys():
            vals_wd = UKV_vals['wind_direction']
            vals_ws = UKV_vals['wind_speed']
            times = UKV_time[key]

            df = pd.DataFrame.from_dict({'time': times, 'wind_speed': vals_ws, 'wind_direction': vals_wd})
            df = df.set_index('time')
            list_of_UKV_df.append(df)

    UKV_df = pd.concat(list_of_UKV_df, axis=1)

    return UKV_df
