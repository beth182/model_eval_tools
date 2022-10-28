import os
from calendar import isleap
import datetime as dt

from scint_flux import look_up as sf_lookup

from model_eval_tools import look_up


def UKV_setup_run(scint_path, variable, DOYstart_choice, DOYstop_choice):
    """
    Function which sets-up directory and variables before the retrieval process.
    """

    # ToDo: check why obs site is used - is it to determine model grid? Or is it not needed?
    # ToDo: check why instrument is needed. Doesn't seem relevant

    obs_site = sf_lookup.scint_path_numbers[scint_path].split('_')[-1]
    instrument = sf_lookup.pair_instruments[sf_lookup.scint_path_numbers[scint_path]]

    if instrument == 'LASMkII_29' or instrument == 'LASMkII_28':
        instrument_string = 'LASMkII_Fast'
    elif instrument == 'BLS':
        instrument_string = 'BLS'
    else:
        raise ValueError('instrument not possible.')

    # construct save folder
    folder_name = str(DOYstart_choice) + '_' + str(DOYstop_choice) + '_' + variable + '_' + obs_site + '_' + str(
        scint_path) + '/'
    save_folder_relative = '../../plots/' + folder_name

    current_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/'

    save_folder = current_dir + save_folder_relative

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    return {'instrument': instrument_string, 'site': obs_site, 'save_folder': save_folder}


def UKV_return_model_DOY(DOYstart, DOYstop, run):
    """
    A function to return a DOY in UKV "language" - as this may change depending on forecast start time.
    """

    # if the files are from the 21Z run, then we need to pick files from the DOY before the chosen range
    # this is because we discount the first 3 hours of the files, so we start at midnight the day after the startDOY...
    if run == '21Z':
        # string out of the chosen starting DOY and year
        str_year = str(DOYstart)[:4]
        str_DOY = str(DOYstart)[4:]
        # if the start DOY is the first day of the year:
        if str_DOY == '001':
            # we now have to start with the year before the chosen year
            new_start_year = int(str_year) - 1
            # to get the start DOY, we need to know what the last DOY of the previous year is
            # so is it a leap year (366 days) or not?
            if isleap(new_start_year):
                # leap year
                new_start_DOY = 366
            else:
                # normal year
                new_start_DOY = 365
            # combining the new start year and new DOY start
            DOYstart_mod = int(str(new_start_year) + str(new_start_DOY))
        else:
            new_start_DOY = str(int(str_DOY) - 1).zfill(3)
            DOYstart_mod = int(str_year + new_start_DOY)
    else:
        DOYstart_mod = DOYstart
    DOYstop_mod = DOYstop - 1

    return {'DOYstart_mod': DOYstart_mod, 'DOYstop_mod': DOYstop_mod}


def UKV_z0_zd(site,
              z0_1_tile=1,
              z0_MORUSES=0.8,
              ):
    """
    Looks up and stores roughness length (z0) and displacement height (zd) for the UKV model (for given LUMO site)
    in a dict to return.
    :param site: LUMO site code
    :param z0_1_tile: z0 for the 1-tile = 1
    :param z0_MORUSES: z0 for MORUSES = 0.8
    :return:
    """

    # look up z0 and zd for the site - values cast as "observed" values
    # z0 and zd calculated in UMEP, using the McDonald 1998 method, and using a source area of 500 m.
    z0_obs = look_up.obs_z0_macdonald[site]
    zd_obs = look_up.obs_zd_macdonald[site]

    roughness_dict = {'z0_1_tile': z0_1_tile, 'z0_MORUSES': z0_MORUSES,
                      'z0_obs': z0_obs, 'zd_obs': zd_obs,
                      'z0_zd_obs': z0_obs + zd_obs}  # z0_zd_obs = combination of z0 and zd for observations

    return roughness_dict


def retrieve_SA_hours(sa_dir_in, DOY):
    """
    Function to construct a list of datetime objects based on what SA files are avail.
    :param sa_dir_in:
    :param DOY:
    :return:
    """

    sa_filenames = []
    for file in os.listdir(sa_dir_in):
        if file.endswith(".tif"):
            sa_filenames.append(file)

    date = dt.datetime.strptime(str(DOY), '%Y%j')
    datetime_list = []

    for filename in sa_filenames:
        # just get the hour as string
        hour_string = filename.split('_')[-2]

        # add this number of hours to the date object, to get datetime of that hour
        assert date.hour == 0
        timedelta = dt.timedelta(hours=int(hour_string))
        new_datetime = date + timedelta

        datetime_list.append(new_datetime)

    return datetime_list


def find_source_area(time,
                     in_dir='C:/Users/beths/Desktop/LANDING/fp_output/hourly/',
                     name_start='BCT_IMU_15000_'):
    """
    Function to find a given time's source area tif file.
    """

    sa_paths = []

    for hour in time:
        # find path
        sa_path = in_dir + name_start + hour.strftime('%Y') + '_' + hour.strftime('%j') + '_' + hour.strftime(
            '%H') + '_' + hour.strftime('%M') + '.tif'
        sa_paths.append(sa_path)

    return sa_paths
