import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from matplotlib.dates import DateFormatter
import netCDF4 as nc
import pylab
from matplotlib import pyplot

from model_eval_tools import look_up


def find_altitude(site,
                  model):
    """
    Function to feed model altitude into sort models
    :param site: site in the format taken from the site_format dict in variables
    :param model: which model I am looking to get altitude for
    :return: altitude
    """

    if model == 'ukv':
        altitude = look_up.UKV_site_altitudes[site]
    elif model == 'lon' or model == 'mor':
        altitude = look_up.LON_site_altitudes[site]
    else:
        raise ValueError('model choice not an option.')

    return altitude


def time_to_datetime(tstr,
                     timeRaw):
    """
    Elliott's function to create datetime objects from the model
    Convert 'time since:... and an array/list of times into a list of datetimes
    :param tstr: string along the lines of 'secs/mins/hours since ........'
    :param timeRaw:
    :return: list of processed times
    EW: 13/03/17
    """
    # sort out times and turn into datetimes
    # tstr = datafile.variables['time'].units
    tstr = tstr.replace('-', ' ')
    tstr = tstr.split(' ')
    # Datetime
    # ---------------
    # create list of datetimes for export
    # start date in netCDF file
    start = dt.datetime(int(tstr[2]), int(tstr[3]), int(tstr[4]))
    if tstr[0] == 'seconds':
        # get delta times from the start date
        # time: time in minutes since the start time (taken from netCDF file)
        delta = [dt.timedelta(seconds=int(timeRaw[i])) for i in range(0, len(timeRaw))]
    elif tstr[0] == 'minutes':
        delta = [dt.timedelta(seconds=int(timeRaw[i] * 60)) for i in range(0, len(timeRaw))]
    elif tstr[0] == 'hours':
        delta = [dt.timedelta(seconds=int(timeRaw[i] * 3600)) for i in range(0, len(timeRaw))]
    if 'delta' in locals():
        return [start + delta[i] for i in np.arange(0, len(timeRaw))]
    else:
        print('Raw time not in seconds, minutes or hours. No processed time created.')
        return


def plotCollection(ax, xs, ys, *args, **kwargs):
    """
    function to group labels in the plots -- otherwise, the same label will appear multiple times
    as it gives one to each file/day being looped over
    :param ax:
    :param xs:
    :param ys:
    :param args:
    :param kwargs:
    :return:
    """

    ax.plot(xs, ys, *args, **kwargs)
    if "label" in kwargs.keys():
        # remove duplicates
        handles, labels = plt.gca().get_legend_handles_labels()
        newLabels, newHandles = [], []
        for handle, label in zip(handles, labels):
            if label not in newLabels:
                newLabels.append(label)
                newHandles.append(handle)
        # pyplot.legend(newHandles, newLabels, loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=12)
        plt.legend(newHandles, newLabels, bbox_to_anchor=(1, 0.5), fontsize=15, loc='center left')


def extract_model_data(files,
                       DOYstart,
                       DOYstop,
                       variable,
                       model_name,
                       target_height,
                       sitechoice,
                       savestring,
                       grid_choice=0,
                       hoursbeforerepeat=24):
    """
    Read premade model files, and extract wanted data from them.

    :param variable: choice of variable. Entered as a string. eg 'Tair'
    :param model: choice of model. Entered as a string. Can be 'ukv' or 'lon' for the London model.
    :param files: dictionaries of filepaths of data to be read in.
    :param target_height: Height of observation, given from the function observations, after adjusting for roughness
        length and displacement height. This is used to find the model level at which the comparison is being made.
    :param DOYstart: date choices, where DOY is day of year. Start of date range.
        This is to be entered as a normal number, i.e. do not wrap one didget DOYs with 0's
        (example: DOY one is 1, and not 001).
    :param DOYstop: date choices, where DOY is day of year. End of date range. (Also, see above for DOYstart format).
    :param sitechoice: Choice of site. This is entered as a string.
    :param savestring: Where to save the plots produced.
    :param grid_choice:
    :param hoursbeforerepeat: this is used to get rid of the repeated items in the model plots - as, in each time,
        datetimes are repeated (as the model files aren't 24 hours, they're 37 hours, and are run again every 24 hours,
        leaving 13 hours of repeat each time). Entered as a number. Typically 24

    :return time_dict: Dictionary of lists of time values for each file.
    :return var_dict: Dictionary of lists of variable chosen values for each file.
    :return var_dict_9: Dictionary of lists of variable chosen values for each file. - this is averaged over all 9
        grid boxes, to compare to the case of just the centre grid values.
    :return var_dict_0: Dictionary of lists of time values for each file. This is the level below the chosen
        model level.
    :return var_dict_2: Dictionary of lists of time values for each file. This is the level above the chosen model
        level.
    :return key_name_times: List of strings of keys in the time_dict, to call in order when plotting.
    :return key_names_vars: List of strings of keys in the var_dict, to call in order when plotting.
    :return key_names_vars_9: List of strings of keys in the var_dict_9, to call in order when plotting.
    :return key_names_vars_0: List of strings of keys in the var_dict_0, to call in order when plotting.
    :return key_names_vars_2: List of strings of keys in the var_dict_2, to call in order when plotting.
    :return height_value: Chosen model level height.
    :return height_value_0: Height below chosen model level height.
    :return height_value_2: Height above chosen model level height.
    :return all_times: List of all times included for all files.
    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Sorting Model: ' + str(model_name))
    print(' ')

    # if there are no model files
    if len(files) == 0:
        print('No files for model:', model_name)
        time_dict = []
        var_dict = []
        var_dict_9 = []
        var_dict_0 = []
        var_dict_2 = []
        key_name_times = []
        key_names_vars = []
        key_names_vars_9 = []
        key_names_vars_0 = []
        key_names_vars_2 = []
        height_value = []
        height_value_0 = []
        height_value_2 = []
        all_times = []

        return (time_dict,
                var_dict,
                var_dict_9,
                var_dict_0,
                var_dict_2,
                key_name_times,
                key_names_vars,
                key_names_vars_9,
                key_names_vars_0,
                key_names_vars_2,
                height_value,
                height_value_0,
                height_value_2,
                all_times)

    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    ####################################################################################################################
    #                                                     SORT MODELS
    ####################################################################################################################
    # creates lists to plot outside of the for loop
    time_dict = {}
    for item in files.keys():
        varname = "time_" + str(item)
        time_dict[varname] = []
        time_dict[varname].append('placeholder')
    var_dict = {}
    for item in files.keys():
        varname = "var_" + str(item)
        var_dict[varname] = []
        var_dict[varname].append('placeholder')

    # Creating a list to keep track of any dodgy model files with large time arrays when converting to datetime
    dodgy_files = []

    # all 9 grids temp - to average all the grids, rather than just take the centre grid
    # all variables associated with this include '9' in the variable name, due to there being 9 grids
    var_dict_9 = {}
    for item in files.keys():
        varname = "var_9_" + str(item)
        var_dict_9[varname] = []
        var_dict_9[varname].append('placeholder')

    # adding the height above and below:
    var_dict_0 = {}
    for item in files.keys():
        varname = "var_0_" + str(item)
        var_dict_0[varname] = []
        var_dict_0[varname].append('placeholder')
    var_dict_2 = {}
    for item in files.keys():
        varname = "var_2_" + str(item)
        var_dict_2[varname] = []
        var_dict_2[varname].append('placeholder')

    # loops over the model file paths in the model filepath dictionary (to import the data each time), and the empty
    # lists ready in var_dict, var_dict_9 (for 3x3 average) and time_dict
    # these will be dictionaries including lists full of values and time respectively,
    # one list for each day/ file in the observation files
    for item, var, time, var_9, var_0, var_2 in zip(sorted(files.values()),
                                                    sorted(var_dict),
                                                    sorted(time_dict),
                                                    sorted(var_dict_9),
                                                    sorted(var_dict_0),
                                                    sorted(var_dict_2)):
        # assigns model .nc file
        file_path = item

        # CHANGED 06/08/18 AS ONE OF THE FILES WAS CORRUPTED, AND COULDN'T BE READ BY NETCDF
        try:
            nc_file = nc.Dataset(file_path)

        except IOError:
            print('PROBLEM READING FILE:')
            print(file_path)
            print("It's size may be 0, and netCDF may have troubles opening corrupted file.")
            dodgy_files.append(file_path)
            continue

        # reads in model height
        # Read in the model data heights. As data is 3x3 grid, take the central
        # cell which overlays the observation location.

        # finding the altitude from the model
        site_format = look_up.premade_model_site_codes[sitechoice]
        # finds altitude from function
        altitude = find_altitude(site_format, model_name)

        if variable == 'BL_H':

            # ToDo: whats going on here? Why am I missing some lines which other level stash codes have?
            # why am I not including altitude here?
            model_heights = nc_file.variables['level_height'][:]

        else:
            # model level variables
            if variable == 'Tair' or variable == 'RH' or variable == 'Press':

                try:
                    model_heights = nc_file.variables['level_height'][:] + altitude
                except KeyError as error:
                    dodgy_files.append(file_path)
                    print(' ')
                    print('ERROR HERE: ', file_path)
                    print("Could not read in ", error, " as this is not a variable in the file")
                    print(' ')
                    continue

            # surface level variables
            elif variable == 'kdown' or variable == 'kup' or variable == 'ldown' or variable == 'lup' or variable == 'H' or variable == 'LE' or variable == 'lstar':
                model_heights = np.zeros(70)[:] + altitude

            else:
                raise ValueError('Variable: ', variable, ' not an option.')

        # finds the closest value of model height to observation, and saves the index
        # if there is no observation files, disheight will be returned as an empty list. So this list is replaced by
        # 10 m, in order to still plot model files if they exist.
        if target_height == []:
            target_height = 10

        # ToDo: check these methods - old (using z0) and new (using target_height)
        # where model_options[model][2] is z0_index
        # z0_index = look_up.model_options[model][2]
        # height_index = np.abs(model_heights - (disheight + z0zd[z0_index])).argmin()

        height_index = np.abs(model_heights - target_height).argmin()

        # if 1D, won't have to unravel: heightindex = np.unravel_index(heightindex, np.shape(modheight))
        height_value = model_heights[height_index]

        # taking the next closest heights
        height_index_0 = height_index - 1
        height_index_2 = height_index + 1
        height_value_0 = model_heights[height_index_0]
        height_value_2 = model_heights[height_index_2]

        # reads in time
        # get time units for time conversion and start time
        unit_start_time = nc_file.variables['time'].units

        # Read in minutes since the start time and add it on
        # Note: time_to_datetime needs time_since to be a list. Hence put value inside a single element list first
        time_since_start = [np.squeeze(nc_file.variables['forecast_reference_time'])]

        # create start time for model data
        # time_to_datetime outputs a list of datetimes, so remove the single element from the list.
        # time to datetime is an imported function
        # Having to put a try/except in here, because some of the model files are dodgy and give huge time arrays
        # when converting to datetime
        try:
            run_start_time = time_to_datetime(unit_start_time, time_since_start)[0]
        except:
            dodgy_files.append(file_path)
            print('DODGY FILE: TIME ARRAY NOT AS EXPECTED: ', np.shape(unit_start_time))
            continue

        # get number of forecast hours to add onto time_start
        run_len_hours = np.squeeze(nc_file.variables['forecast_period'][:])

        run_times = [run_start_time + dt.timedelta(seconds=hr * 3600) for hr in run_len_hours]

        # KSSW is a site with more letters than others, so it's handled differently when finding the date:
        if sitechoice == 'KSSW':
            start_index = -34
            end_index = -26
        elif sitechoice == 'BFCL':
            start_index = -34
            end_index = -26
        elif sitechoice == 'MR':
            start_index = -32
            end_index = -24
        elif sitechoice == 'NK':
            start_index = -32
            end_index = -24
        else:
            start_index = -33
            end_index = -25

        # DIFFERENT LENGTHS OF FILES...

        # constructing midnight
        # seen in ukv files
        midnight_date = dt.datetime.strptime(str(file_path[start_index:end_index]), '%Y%m%d') + dt.timedelta(
            days=1)
        midnight = dt.time(0, 0)
        midnight_datetime = dt.datetime.combine(midnight_date, midnight)

        # constructing 21 Z
        correct_date = dt.datetime.strptime(str(file_path[start_index:end_index]), '%Y%m%d')
        correct_time = dt.time(21, 0)
        correct_datetime = dt.datetime.combine(correct_date, correct_time)

        # constructing 10 pm
        # seen in lon files
        ten_date = dt.datetime.strptime(str(file_path[start_index:end_index]), '%Y%m%d')
        ten_time = dt.time(22, 0)
        ten_datetime = dt.datetime.combine(ten_date, ten_time)

        # if the time isn't exactly on the hour
        if run_times[0].minute != 0 or run_times[0].second != 0 or run_times[0].microsecond != 0:
            for i, item in enumerate(run_times):
                # Rounds to nearest hour by adding a timedelta hour if minute >= 30
                new_t = item.replace(second=0, microsecond=0, minute=0, hour=item.hour) + dt.timedelta(
                    hours=item.minute // 30)

                # if the difference between the time and the nearest hour is less than a minute and a half:
                if abs(item - new_t) < dt.timedelta(minutes=1.5):
                    run_times[i] = new_t
                else:
                    print('ERROR: DODGY FILE: ', file_path)
                    print('THERE IS A TIME WITH A LARGER DIFFERENCE THAN 1.5 MINUTES TO THE HOUR: ', item)
                    dodgy_files.append(file_path)
                    continue

        # Do the model times start where they should? should start at 2100, and I want to take all values from after
        # the first 3 hours (allowing for spin up) - so ideally times should start at midnight for a perfect file
        if run_times[0] == correct_datetime:
            # index to start defined here, as different situations have a different start index.
            # and these need to be considered when taking values, too. Otherwise, list lengths will be different.
            index_to_start = 3
        # if the file starts at midnight, don't need to adjust for spin up (as this is already not taking first
        # 3 hours)
        elif run_times[0] == midnight_datetime:
            index_to_start = 0
        # some files start at 10 pm? so therefore neglect forst 2 hours instead of 3 hours
        elif run_times[0] == ten_datetime:
            index_to_start = 2

        else:
            print(' ')
            print('ERROR: DODGY FILE: previously unseen time length in this file: ', file_path)
            print(len(run_times), 'start:', run_times[0], 'end:', run_times[-1])
            print(' ')
            dodgy_files.append(file_path)
            continue

        model_time = run_times[index_to_start:index_to_start + hoursbeforerepeat]

        # check to see if all hours are consecutive by 1 hour...
        flag = 0
        for i in range(0, len(model_time) - 1):
            if model_time[i + 1] == model_time[i] + dt.timedelta(hours=1):
                pass
            else:
                print(' ')
                print('ERROR: There is a jump in hours: ')
                print(model_time[i], model_time[i + 1])
                print('For file: ' + file_path)
                flag = 1
        if flag == 1:
            dodgy_files.append(file_path)
            continue

        # Makes a choice about which grid to use. For NEW file format:
        # Defult grid choice is always 0 - this means centre grid is chosen (lat and lon idex both 1 - middle of 3x3
        # of it's a letter, grid lon and lat defined here:
        if grid_choice == 0:
            # Defult val goes to centre grid, otherwise known as grid 'E':
            index_lat = 1
            index_lon = 1

        elif grid_choice == 'A':
            index_lat = 2
            index_lon = 0
        elif grid_choice == 'B':
            index_lat = 2
            index_lon = 1
        elif grid_choice == 'C':
            index_lat = 2
            index_lon = 2
        elif grid_choice == 'D':
            index_lat = 1
            index_lon = 0
        elif grid_choice == 'E':
            index_lat = 1
            index_lon = 1
        elif grid_choice == 'F':
            index_lat = 1
            index_lon = 2
        elif grid_choice == 'G':
            index_lat = 0
            index_lon = 0
        elif grid_choice == 'H':
            index_lat = 0
            index_lon = 1
        elif grid_choice == 'I':
            index_lat = 0
            index_lon = 2
        else:
            raise ValueError('Grid choice: ', grid_choice, ' not an option.')

        # READS IN VALUES
        if variable == 'Tair':
            # reads in temperatures
            model_vars = nc_file.variables['air_temperature']
            # finds temperature values at the closest model height to obs
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index] - 273.15

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_0] - 273.15
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_2] - 273.15

        elif variable == 'RH':
            # reads in relative humidity
            model_vars = nc_file.variables['relative_humidity']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index]

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_0]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_2]

        elif variable == 'Press':
            # reads in Press
            model_vars = nc_file.variables['air_pressure']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index] / 100.

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_0] / 100.
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_2] / 100.

        elif variable == 'kdown':
            # reads in incoming shortwave radiation
            model_vars = nc_file.variables['surface_downwelling_shortwave_flux_in_air']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            # taking the next closest heights
            # ToDo: this step is unnecessary for all surface stash codes
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

        elif variable == 'ldown':
            # reads in outgoing shortwave radiation
            model_vars = nc_file.variables['surface_downwelling_longwave_flux_in_air']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

        elif variable == 'lstar':
            model_vars = nc_file.variables['surface_net_longwave_flux_in_air']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

        elif variable == 'H':
            try:
                model_vars = nc_file.variables['surface_upward_sensible_heat_flux']
            except:
                model_vars = nc_file.variables['surface_sensible_heat_flux']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

        elif variable == 'BL_H':
            model_vars = nc_file.variables['boundary_layer_heat_fluxes']
            # finds temperature values at the closest model height to obs
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index]

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_0]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                         height_index_2]

        elif variable == 'LE':
            try:
                model_vars = nc_file.variables['surface_upward_latent_heat_flux']
            except:
                model_vars = nc_file.variables['surface_latent_heat_flux']
            var_vals = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

            # taking the next closest heights
            var_vals_0 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]
            var_vals_2 = model_vars[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat]

        else:
            raise ValueError('variable choice not an option')

        # append times to a list to plot outside of the for loop
        for timevalue in model_time:
            time_dict[time].append(timevalue)
        # append temps to a list to plot outside of the for loop
        for value in var_vals:
            var_dict[var].append(value)

        # 3x3 grid average
        shape_number = 2

        for i in range(index_to_start, np.shape(model_vars)[shape_number]):
            if variable == 'Tair':
                var_vals_mean = np.mean(model_vars[:, :, i, height_index] - 273.15)

            elif variable == 'RH':
                var_vals_mean = np.mean(model_vars[:, :, i, height_index])

            elif variable == 'BL_H':
                var_vals_mean = np.mean(model_vars[:, :, i, height_index])

            elif variable == 'Press':
                var_vals_mean = np.mean(model_vars[:, :, i, height_index]) / 100.

            elif variable == 'kdown' or variable == 'kup' or variable == 'ldown' or variable == 'lup' or variable == 'lstar':
                var_vals_mean = np.mean(model_vars[:, :, i])

            elif variable == 'H' or variable == 'LE':
                var_vals_mean = np.mean(model_vars[:, :, i])

            else:
                raise ValueError('variable choice not an option.')

            # append temps9 to a list to plot outside of the for loop
            var_dict_9[var_9].append(var_vals_mean)

        # fromliam: [np.mean(model_vars[0,i,height_index,:,:] -273.15) for i in range(37)]

        # taking the next closest heights
        for item0 in var_vals_0:
            var_dict_0[var_0].append(item0)
        for item2 in var_vals_2:
            var_dict_2[var_2].append(item2)

    # ToDo: a check on height value - to make sure it's consistent through the loop and that it is properly defined.

    # print out any dodgy model files with huge time array lengths...
    print('number of dodgy model files:', len(dodgy_files))
    if len(dodgy_files) == 0:
        pass
    else:
        print(dodgy_files)

    # deletes placeholder
    for item in var_dict:
        if var_dict[item][0] == 'placeholder':
            del var_dict[item][0]
    for item in time_dict:
        if time_dict[item][0] == 'placeholder':
            del time_dict[item][0]
    for item in var_dict_9:
        if var_dict_9[item][0] == 'placeholder':
            del var_dict_9[item][0]
    for item in var_dict_0:
        if var_dict_0[item][0] == 'placeholder':
            del var_dict_0[item][0]
    for item in var_dict_2:
        if var_dict_2[item][0] == 'placeholder':
            del var_dict_2[item][0]

    # names to use for plotting in order - otherwise strange lines appear all over the plot,
    # trying to link datetimes together
    # ToDo: a better system here.
    # ToDo: check if some of these key names are the same (are key names for vars 9, 0, 2, original the same?)
    key_names_vars = []
    for item in sorted(var_dict):
        key_names_vars.append(item)
    key_name_times = []
    for item in sorted(time_dict):
        key_name_times.append(item)
    key_names_vars_9 = []
    for item in sorted(var_dict_9):
        key_names_vars_9.append(item)
    # heights 0 and 2
    key_names_vars_0 = []
    for item in sorted(var_dict_0):
        key_names_vars_0.append(item)
    key_names_vars_2 = []
    for item in sorted(var_dict_2):
        key_names_vars_2.append(item)

    # A test to see if there are any repeated times within the London model,
    # as part of the 'strange lines on plot' debugging
    all_times = []
    for item in key_name_times:
        for time in time_dict[item][:hoursbeforerepeat]:
            all_times.append(time)
    print(' ')
    print('Finding any dupulate times:')
    if len(set([x for x in all_times if all_times.count(x) > 1])) == 0:
        print('No duplicates')
    else:
        print(len(set([x for x in all_times if all_times.count(x) > 1])), 'Duplicates')
        repeats = list(set([x for x in all_times if all_times.count(x) > 1]))
        print(repeats)

    # dodgy files dealing with skipping times still for some reason appending the string name to string list. So here,
    # I am being lazy and manually removing any lists with time length 0 before plotting
    for temp, var_all, time in zip(key_names_vars,
                                   key_names_vars_9,
                                   key_name_times
                                   ):

        if len(time_dict[time][:hoursbeforerepeat]) == 0:
            print('There was a time list which has length 0: ', time)

            key_names_vars.remove(temp)
            key_names_vars_9.remove(var_all)
            key_name_times.remove(time)

            # not sure I need these:
            del time_dict[time]
            del var_dict[temp]
            del var_dict_9[var_all]

    # ToDo: option for not plotting here
    # plotting the differences between 3x3 averaged and centre grid
    plt.figure(figsize=(20, 10))
    ax = pyplot.subplot(1, 1, 1)

    mod_colour = look_up.model_options[model_name][1]

    # for temp, time in zip(key_names_vars_9, key_name_times):
    #     plotCollection(ax, time_dict[time][:hoursbeforerepeat], var_dict_9[temp][:hoursbeforerepeat], 'g',
    #                    label="3x3 averaged %s @ %d m" % (model, height_value))

    for temp, time in zip(key_names_vars, key_name_times):
        # plotCollection calling the function that sorts out repeated
        # labels in the legend, defined in the observations section
        plotCollection(ax, time_dict[time][:], var_dict[temp][:], mod_colour,
                       label="%s @ %d m" % (model_name, height_value))

    plt.xlabel('DOY')
    plt.ylabel(label_string)
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_formatter(DateFormatter('%j'))

    date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
    plt.title(sitechoice + ': ' + date_for_title)

    pylab.savefig(savestring + str(variable) + '_' + str(model_name) + '_' + sitechoice + '_' +
                  str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')

    # ToDo: check if all these returns are needed
    # ToDo: return as a dict
    return (time_dict,
            var_dict,
            var_dict_9,
            var_dict_0,
            var_dict_2,
            key_name_times,
            key_names_vars,
            key_names_vars_9,
            key_names_vars_0,
            key_names_vars_2,
            height_value,
            height_value_0,
            height_value_2,
            all_times)
