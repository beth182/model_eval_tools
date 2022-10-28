import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from matplotlib.dates import DateFormatter
import netCDF4 as nc
import pylab
from matplotlib import pyplot

from model_eval_tools import look_up


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

    plt.close('all')

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


def extract_model_data_wind(files,
                            DOYstart,
                            DOYstop,
                            variable,
                            model,
                            target_height,
                            sitechoice,
                            savestring,
                            grid_choice=0,
                            hoursbeforerepeat=24):
    """
    Read premade model files, and extract wanted data from them.
    See extract_model_data for the following:
    :param files:
    :param DOYstart:
    :param DOYstop:
    :param variable:
    :param model:
    :param target_height:
    :param sitechoice:
    :param savestring:
    :param grid_choice:
    :param hoursbeforerepeat:
    :return:
    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Sorting Model Wind: ' + str(model))
    print(' ')

    # if there are no model files
    if len(files) == 0:
        print('No files for model:', model)
        time_dict = []
        wind_dict = []
        dir_dict = []
        key_name_times = []
        key_name_winds = []
        key_name_dirs = []
        height_value = []
        all_times = []
        key_name_winds_9 = []
        key_name_dirs_9 = []
        key_name_winds_0 = []
        key_name_dirs_0 = []
        key_name_winds_2 = []
        key_name_dirs_2 = []
        height_value_0 = []
        height_value_2 = []
        wind_dict_9 = []
        dir_dict_9 = []
        wind_dict_0 = []
        dir_dict_0 = []
        wind_dict_2 = []
        dir_dict_2 = []
        return (time_dict,
                wind_dict,
                dir_dict,
                key_name_times,
                key_name_winds,
                key_name_dirs,
                height_value,
                all_times,
                key_name_winds_9,
                key_name_dirs_9,
                key_name_winds_0,
                key_name_dirs_0,
                key_name_winds_2,
                key_name_dirs_2,
                height_value_0,
                height_value_2,
                wind_dict_9,
                dir_dict_9,
                wind_dict_0,
                dir_dict_0,
                wind_dict_2,
                dir_dict_2)

    assert variable == 'wind'

    # choices dependent on variable choice
    label_string = look_up.variable_info[variable][0]

    ####################################################################################################################
    #                                                     WIND
    ####################################################################################################################
    # MORE THAN ONE STASH CODE INCLUDED FOR THIS VARIABLE
    u_index_for_files = 0
    v_index_for_files = 1

    # creates lists to plot outside of the for loop
    time_dict = {}
    for item in files[0].keys():
        varname = "time_" + str(item)
        time_dict[varname] = []
        time_dict[varname].append('placeholder')
    # speed
    wind_dict = {}
    for item in files[0].keys():
        varname = "wind_" + str(item)
        wind_dict[varname] = []
        wind_dict[varname].append('placeholder')
    # dir
    dir_dict = {}
    for item in files[0].keys():
        varname = "dir_" + str(item)
        dir_dict[varname] = []
        dir_dict[varname].append('placeholder')

    # Creating a list to keep track of any dodgy model files with large time arrays when converting to datetime
    dodgy_files = []

    # all 9 grids temp - to average all the grids, rather than just take the centre grid
    # all variables associated with this include '9' in the variable name, due to there being 9 grids
    wind_dict_9 = {}
    for item in files[0].keys():
        varname = "wind_9_" + str(item)
        wind_dict_9[varname] = []
        wind_dict_9[varname].append('placeholder')

    dir_dict_9 = {}
    for item in files[0].keys():
        varname = "dir_9_" + str(item)
        dir_dict_9[varname] = []
        dir_dict_9[varname].append('placeholder')

    # adding the height above and below:
    wind_dict_0 = {}
    for item in files[0].keys():
        varname = "wind_0_" + str(item)
        wind_dict_0[varname] = []
        wind_dict_0[varname].append('placeholder')
    wind_dict_2 = {}
    for item in files[0].keys():
        varname = "wind_2_" + str(item)
        wind_dict_2[varname] = []
        wind_dict_2[varname].append('placeholder')

    dir_dict_0 = {}
    for item in files[0].keys():
        varname = "dir0" + str(item)
        dir_dict_0[varname] = []
        dir_dict_0[varname].append('placeholder')
    dir_dict_2 = {}
    for item in files[0].keys():
        varname = "dir2" + str(item)
        dir_dict_2[varname] = []
        dir_dict_2[varname].append('placeholder')

    # loops over the london model file paths in obvsdict (to import the data each time), and the empty
    # lists ready in lonswinddict,and time_dict, dir_dict (plus 3x3 average and 2nd height lists)
    # these will be dictionaries including lists full of values and time respectively,
    # one list for each day/ file in the observation files
    for uitem, vitem, wind, time, direction, wind_9, dir_9, wind_0, wind_2, dir_0, dir_2 in zip(
            sorted(files[u_index_for_files].values()),
            sorted(files[v_index_for_files].values()),
            sorted(wind_dict),
            sorted(time_dict),
            sorted(dir_dict),
            sorted(wind_dict_9),
            sorted(dir_dict_9),
            sorted(wind_dict_0),
            sorted(wind_dict_2),
            sorted(dir_dict_0),
            sorted(dir_dict_2)):

        # assigns model .nc file
        file_path_u = uitem
        file_path_v = vitem

        # CHANGED 06/08/18 AS ONE OF THE FILES WAS CORRUPTED, AND COULDN'T BE READ BY NETCDF
        # nc_file_u = nc.Dataset(file_path_u)
        # nc_file_v = nc.Dataset(file_path_v)
        try:
            nc_file_u = nc.Dataset(file_path_u)
        except IOError:
            print('PROBLEM READING FILE:')
            print(file_path_u)
            print("It's size may be 0, and netCDF may have troubles opening corrupted file.")
            dodgy_files.append(file_path_u)
            continue

        try:
            nc_file_v = nc.Dataset(file_path_v)
        except IOError:
            print('PROBLEM READING FILE:')
            print(file_path_v)
            print("It's size may be 0, and netCDF may have troubles opening corrupted file.")
            dodgy_files.append(file_path_v)
            continue

        # reads in model height
        # Read in the model data heights. As data is 3x3 grid, take the central
        # cell which overlays the observation location.

        # finding the altitude from the model
        site_format = look_up.premade_model_site_codes[sitechoice]
        # finds altitude from function
        altitude = find_altitude(site_format, model)

        try:
            model_heights_u = nc_file_u.variables['level_height'][:] + altitude

        except KeyError as error:
            dodgy_files.append(file_path_u)
            print(' ')
            print('ERROR HERE: ', file_path_u)
            print("Could not read in ", error, " as this is not a variable in the file")
            print(' ')
            continue

        # tests to make sure all files with just one variable (and not time/ height) are caught
        try:
            model_heights_v = nc_file_v.variables['level_height'][:] + altitude
        except KeyError as error:
            dodgy_files.append(file_path_v)
            print(' ')
            print('ERROR HERE: ', file_path_v)
            print("Could not read in ", error, " as this is not a variable in the file")
            print(' ')
            continue

        # check that the heights are the same between stash codes
        assert model_heights_u.all() == model_heights_v.all()

        # finds the closest value of model height to observation, and saves the index
        # if there is no observation files, disheight will be returned as an empty list. So this list is replaced by
        # 10 m, in order to still plot model files if they exist.
        if target_height == []:
            target_height = 10

        # why am I doing this in this function?
        # should be removed and done outside

        # where model_options[model][2] is z0_index
        # z0_index = look_up.model_options[model][2]
        # height_index = np.abs(model_heights_u - (disheight + z0zd[z0_index])).argmin()

        height_index = np.abs(model_heights_u - target_height).argmin()

        # if 1D, won't have to unravel
        height_value = model_heights_u[height_index]

        # taking the next closest heights
        height_index_0 = height_index - 1
        height_index_2 = height_index + 1
        height_value_0 = model_heights_u[height_index_0]
        height_value_2 = model_heights_u[height_index_2]

        # reads in time
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
        midnight_date = dt.datetime.strptime(str(file_path_u[start_index:end_index]), '%Y%m%d') + dt.timedelta(
            days=1)
        midnight = dt.time(0, 0)
        midnight_datetime = dt.datetime.combine(midnight_date, midnight)

        # constructing 21 Z
        correct_date = dt.datetime.strptime(str(file_path_u[start_index:end_index]), '%Y%m%d')
        correct_time = dt.time(21, 0)
        correct_datetime = dt.datetime.combine(correct_date, correct_time)

        # constructing 10 pm
        # seen in lon files
        ten_date = dt.datetime.strptime(str(file_path_u[start_index:end_index]), '%Y%m%d')
        ten_time = dt.time(22, 0)
        ten_datetime = dt.datetime.combine(ten_date, ten_time)

        # NEED TO DO TIMES TWICE FOR BOTH STASH CODE FILES TO SEE IF I HAVE THE SAME TIMES!
        # ----------------------------------------------------------------------------------------------------------
        # U
        # get time units for time conversion and start time
        unit_start_time_u = nc_file_u.variables['time'].units

        # Read in minutes since the start time and add it on
        # Note: time_to_datetime needs time_since to be a list. Hence put value inside a single element list first
        time_since_start_u = [np.squeeze(nc_file_u.variables['forecast_reference_time'])]

        # create start time for model data
        # time_to_datetime outputs a list of datetimes, so remove the single element from the list.
        # time to datetime is an imported function
        # Having to put a try/except in here, because some of the model files are dodgy and gove huge time arrays
        # when converting to datetime
        try:
            run_start_time_u = time_to_datetime(unit_start_time_u, time_since_start_u)[0]
        except:
            dodgy_files.append(file_path_u)
            print('DODGY FILE: TIME ARRAY NOT AS EXPECTED: ', np.shape(unit_start_time_u))
            continue

        # get number of forecast hours to add onto time_start
        run_len_hours_u = np.squeeze(nc_file_u.variables['forecast_period'][:])

        run_times_u = [run_start_time_u + dt.timedelta(seconds=hr * 3600) for hr in run_len_hours_u]

        # if the time isn't exactly on the hour
        if run_times_u[0].minute != 0 or run_times_u[0].second != 0 or run_times_u[0].microsecond != 0:
            for i, item in enumerate(run_times_u):
                # Rounds to nearest hour by adding a timedelta hour if minute >= 30
                new_t = item.replace(second=0, microsecond=0, minute=0, hour=item.hour) + dt.timedelta(
                    hours=item.minute // 30)

                # if the difference between the time and the nearest hour is less than a minute and a half:
                if abs(item - new_t) < dt.timedelta(minutes=1.5):
                    run_times_u[i] = new_t
                else:
                    print('ERROR: DODGY FILE: ', file_path_u)
                    print('THERE IS A TIME WITH A LARGER DIFFERENCE THAN 1.5 MINUTES TO THE HOUR: ', item)
                    dodgy_files.append(file_path_u)
                    continue

        # does the model times start where it should? should start at 9, and I want to take all values from after
        # the first 3 hours (allowing for spin up) - so ideally times should start at midnight for a perfect file
        if run_times_u[0] == correct_datetime:
            # index to start defined here, as different situations have a different start index.
            # and these need to be considered when taking values, too. Otherwise, list lengths will be different.
            index_to_start = 3
        # if the file starts at midnight, don't need to adjust for spin up (as this is already not taking first
        # 3 hours)
        elif run_times_u[0] == midnight_datetime:
            index_to_start = 0
        # some files start at 10 pm? so therefore neglect forst 2 hours instead of 3 hours
        elif run_times_u[0] == ten_datetime:
            index_to_start = 2

        else:
            print(' ')
            print('ERROR: DODGY FILE: previously unseen time length in this file: ', file_path_u)
            print(len(run_times_u), 'start:', run_times_u[0], 'end:', run_times_u[-1])
            print(' ')
            dodgy_files.append(file_path_u)
            continue

        model_time_u = run_times_u[index_to_start:index_to_start + hoursbeforerepeat]

        # check to see if all hours are consecutive by 1 hour...
        flag = 0
        for i in range(0, len(model_time_u) - 1):
            if model_time_u[i + 1] == model_time_u[i] + dt.timedelta(hours=1):
                pass
            else:
                print(' ')
                print('ERROR: There is a jump in hours: ')
                print(model_time_u[i], model_time_u[i + 1])
                print('For file: ' + file_path_u)

                flag = 1

        if flag == 1:
            dodgy_files.append(file_path_u)
            continue

        # ----------------------------------------------------------------------------------------------------------
        # V
        # get time units for time conversion and start time
        unit_start_time_v = nc_file_v.variables['time'].units

        # Read in minutes since the start time and add it on
        # Note: time_to_datetime needs time_since to be a list. Hence put value inside a single element list first
        time_since_start_v = [np.squeeze(nc_file_v.variables['forecast_reference_time'])]

        # create start time for model data
        # time_to_datetime outputs a list of datetimes, so remove the single element from the list.
        # time to datetime is an imported function
        # Having to put a try/except in here, because some of the model files are dodgy and gove huge time arrays
        # when converting to datetime
        try:
            run_start_time_v = time_to_datetime(unit_start_time_v, time_since_start_v)[
                0]  # time_to_datetime is a
            # function defined at top
        except:
            dodgy_files.append(file_path_v)
            print('DODGY FILE: TIME ARRAY NOT AS EXPECTED: ', np.shape(unit_start_time_v))
            continue

        # get number of forecast hours to add onto time_start
        run_len_hours_v = np.squeeze(nc_file_v.variables['forecast_period'][:])

        run_times_v = [run_start_time_v + dt.timedelta(seconds=hr * 3600) for hr in run_len_hours_v]

        # if the time isn't exactly on the hour
        if run_times_v[0].minute != 0 or run_times_v[0].second != 0 or run_times_v[0].microsecond != 0:
            for i, item in enumerate(run_times_v):
                # Rounds to nearest hour by adding a timedelta hour if minute >= 30
                new_t = item.replace(second=0, microsecond=0, minute=0, hour=item.hour) + dt.timedelta(
                    hours=item.minute // 30)

                # if the difference between the time and the nearest hour is less than a minute and a half:
                if abs(item - new_t) < dt.timedelta(minutes=1.5):
                    run_times_v[i] = new_t
                else:
                    print('ERROR: DODGY FILE: ', file_path_v)
                    print('THERE IS A TIME WITH A LARGER DIFFERENCE THAN 1.5 MINUTES TO THE HOUR: ', item)
                    dodgy_files.append(file_path_v)
                    continue

        # does the model times start where it should? should start at 9, and I want to take all values from after
        # the first 3 hours (allowing for spin up) - so ideally times should start at midnight for a perfect file
        if run_times_v[0] == correct_datetime:
            # index to start defined here, as different situations have a different start index.
            # and these need to be considered when taking values, too. Otherwise, list lengths will be different.
            index_to_startv = 3
        # if the file starts at midnight, don't need to adjust for spin up (as this is already not taking first
        # 3 hours)
        elif run_times_v[0] == midnight_datetime:
            index_to_startv = 0
        # some files start at 10 pm? so therefore neglect forst 2 hours instead of 3 hours
        elif run_times_v[0] == ten_datetime:
            index_to_startv = 2

        else:
            print(' ')
            print('ERROR: DODGY FILE: previously unseen time length in this file: ', file_path_v)
            print(len(run_times_v), 'start:', run_times_v[0], 'end:', run_times_v[-1])
            print(' ')
            dodgy_files.append(file_path_v)
            continue

        model_time_v = run_times_v[index_to_startv:index_to_startv + hoursbeforerepeat]

        # check to see if all hours are consecutive by 1 hour...
        flag = 0
        for i in range(0, len(model_time_v) - 1):
            if model_time_v[i + 1] == model_time_v[i] + dt.timedelta(hours=1):
                pass
            else:
                print(' ')
                print('ERROR: There is a jump in hours: ')
                print(model_time_v[i], model_time_v[i + 1])
                print('For file: ' + file_path_v)

                flag = 1

        if flag == 1:
            dodgy_files.append(file_path_v)
            continue

        # ----------------------------------------------------------------------------------------------------------
        # TIME TESTS BETWEEN THE TWO LISTS TO SEE IF THEY ARE THE SAME
        # if the 2 time lists start at the same time:
        if model_time_u[0] == model_time_v[0]:
            # if the 2 lists are the same length
            if len(model_time_u) == len(model_time_v):
                time_test_pass = True
            # if the two lists are not the same length
            else:
                time_test_pass = False
                # find all the indexes of items that are in one list but not the other
                # first way round
                index_list_uv = []
                for i, item in enumerate(model_time_u):
                    if item in model_time_v:
                        pass
                    else:
                        index_list_uv.append(i)
                # second way round
                index_list_vu = []
                for i, item in enumerate(model_time_v):
                    if item in model_time_u:
                        pass
                    else:
                        index_list_vu.append(i)

                # if both lists have items in the index list, there is a problem
                if len(index_list_uv) != 0 and len(index_list_vu) != 0:
                    raise ValueError("Both time lists have items that the other one doesn't!")

                # define the first index of an item that is on one and not the other
                if len(index_list_uv) == 0:
                    pass
                else:
                    index_diff = index_list_uv[0]

                if len(index_list_vu) == 0:
                    pass
                else:
                    index_diff = index_list_vu[0]

        else:
            raise ValueError('The two time lists do not start with the same time!', model_time_u[0], model_time_v[0])

        # ----------------------------------------------------------------------------------------------------------
        # Makes a choice about which grid to use.
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

        # ----------------------------------------------------------------------------------------------------------

        # READS IN VALUES
        # reads in u and v components of wind speed and direction
        model_vars_u = nc_file_u.variables['eastward_wind']
        model_vars_v = nc_file_v.variables['northward_wind']

        # finds wind values at the closest model height to obs
        var_vals_u = model_vars_u[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                     height_index]
        var_vals_v = model_vars_v[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                     height_index]

        # taking the next closest heights
        var_vals_u_0 = model_vars_u[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index_0]
        var_vals_u_2 = model_vars_u[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index_2]
        var_vals_v_0 = model_vars_v[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index_0]
        var_vals_v_2 = model_vars_v[index_lat, index_lon, index_to_start:index_to_start + hoursbeforerepeat,
                       height_index_2]

        # calculates wind speed and direction from u and v componants
        if time_test_pass:
            pass
        else:
            var_vals_v = var_vals_v[:index_diff - 1]
            var_vals_u = var_vals_u[:index_diff - 1]

        var_vals_wind = ((var_vals_u ** 2) + (var_vals_v ** 2)) ** 0.5
        # http://weatherclasses.com/uploads/4/2/8/6/4286089/computing_wind_direction_and_speed_from_u_and_v.pdf
        var_vals_dir = np.arctan2(var_vals_u, var_vals_v) * (180.0 / np.pi) + 180.0

        # Ensuring the direction is between 0 and 360 degrees
        for i in range(len(var_vals_dir)):
            if var_vals_dir[i] < 0.0:
                var_vals_dir[i] = var_vals_dir[i] + 360.0
            if var_vals_dir[i] > 360.0:
                var_vals_dir[i] = var_vals_dir[i] - 360.0

        # other heights:
        var_vals_wind_0 = ((var_vals_u_0 ** 2) + (var_vals_v_0 ** 2)) ** 0.5
        var_vals_dir_0 = np.arctan2(var_vals_u_0, var_vals_v_0) * (180.0 / np.pi) + 180.0
        for i in range(len(var_vals_dir_0)):
            if var_vals_dir_0[i] < 0.0:
                var_vals_dir_0[i] = var_vals_dir_0[i] + 360.0
            if var_vals_dir_0[i] > 360.0:
                var_vals_dir_0[i] = var_vals_dir_0[i] - 360.0

        var_vals_wind_2 = ((var_vals_u_2 ** 2) + (var_vals_v_2 ** 2)) ** 0.5
        var_vals_dir_2 = np.arctan2(var_vals_u_2, var_vals_v_2) * (180.0 / np.pi) + 180.0
        for i in range(len(var_vals_dir_2)):
            if var_vals_dir_2[i] < 0.0:
                var_vals_dir_2[i] = var_vals_dir_2[i] + 360.0
            if var_vals_dir_2[i] > 360.0:
                var_vals_dir_2[i] = var_vals_dir_2[i] - 360.0

        # append times to a list to plot outside of the for loop
        for item in model_time_u:
            time_dict[time].append(item)
        # append winds to a list to plot outside of the for loop
        for item in var_vals_wind:
            wind_dict[wind].append(item)
        # append direction to a list to plot outside of the for loop
        for item in var_vals_dir:
            dir_dict[direction].append(item)

        # 3x3 grid average
        shape_number = 2

        u_means = []
        v_means = []
        for i in range(index_to_start, np.shape(model_vars_u)[shape_number]):
            u_mean = np.mean(model_vars_u[:, :, i, height_index])
            v_mean = np.mean(model_vars_v[:, :, i, height_index])
            u_means.append(u_mean)
            v_means.append(v_mean)

        # calculates wind speed and direction from u and v components
        wind_means = []
        dir_means = []
        for umean, vmean in zip(u_means, v_means):
            wind_means_i = ((umean ** 2) + (vmean ** 2)) ** 0.5
            dir_means_i = np.arctan2(umean, vmean) * (180.0 / np.pi) + 180.0
            # Ensuring the direction is between 0 and 360 degrees
            if dir_means_i < 0.0:
                dir_means_i = dir_means_i + 360.0
            if dir_means_i > 360.0:
                dir_means_i = dir_means_i - 360.0

            wind_means.append(wind_means_i)
            dir_means.append(dir_means_i)

        # append averages to a list to plot outside of the for loop
        wind_dict_9[wind_9].append(wind_means)
        dir_dict_9[dir_9].append(dir_means)

        # taking the next closest heights
        for item0 in var_vals_wind_0:
            wind_dict_0[wind_0].append(item0)
        for item2 in var_vals_wind_2:
            wind_dict_2[wind_2].append(item2)
        for item0 in var_vals_dir_0:
            dir_dict_0[dir_0].append(item0)
        for item2 in var_vals_dir_2:
            dir_dict_2[dir_2].append(item2)

    # print out any dodgy model files with huge time array lengths...
    print('number of dodgy model files:', len(dodgy_files))
    if len(dodgy_files) == 0:
        pass
    else:
        print(dodgy_files)

    # deletes placeholder
    for item in wind_dict:
        if wind_dict[item][0] == 'placeholder':
            del wind_dict[item][0]
    for item in time_dict:
        if time_dict[item][0] == 'placeholder':
            del time_dict[item][0]
    for item in dir_dict:
        if dir_dict[item][0] == 'placeholder':
            del dir_dict[item][0]
    for item in wind_dict_9:
        if wind_dict_9[item][0] == 'placeholder':
            del wind_dict_9[item][0]
    for item in dir_dict_9:
        if dir_dict_9[item][0] == 'placeholder':
            del dir_dict_9[item][0]
    for item in wind_dict_0:
        if wind_dict_0[item][0] == 'placeholder':
            del wind_dict_0[item][0]
    for item in wind_dict_2:
        if wind_dict_2[item][0] == 'placeholder':
            del wind_dict_2[item][0]
    for item in dir_dict_0:
        if dir_dict_0[item][0] == 'placeholder':
            del dir_dict_0[item][0]
    for item in dir_dict_2:
        if dir_dict_2[item][0] == 'placeholder':
            del dir_dict_2[item][0]

    # names to use for plotting in order - otherwise strange lines appear all over the plot,
    # trying to link datetimes together
    key_name_times = []
    for item in sorted(time_dict):
        key_name_times.append(item)
    key_name_winds = []
    for item in sorted(wind_dict):
        key_name_winds.append(item)
    key_name_dirs = []
    for item in sorted(dir_dict):
        key_name_dirs.append(item)
    key_name_winds_9 = []
    for item in sorted(wind_dict_9):
        key_name_winds_9.append(item)
    key_name_dirs_9 = []
    for item in sorted(dir_dict_9):
        key_name_dirs_9.append(item)
    key_name_winds_0 = []
    for item in sorted(wind_dict_0):
        key_name_winds_0.append(item)
    key_name_dirs_0 = []
    for item in sorted(dir_dict_0):
        key_name_dirs_0.append(item)
    key_name_winds_2 = []
    for item in sorted(wind_dict_2):
        key_name_winds_2.append(item)
    key_name_dirs_2 = []
    for item in sorted(dir_dict_2):
        key_name_dirs_2.append(item)

    # A test to see if there are any repeated times within the London model, as part of the
    # 'strange lines on plot' debugging
    all_times = []
    for item in key_name_times:
        for time in time_dict[item][:hoursbeforerepeat]:
            all_times.append(time)
    print(' ')
    print('Finding any duplicate times:')
    if len(set([x for x in all_times if all_times.count(x) > 1])) == 0:
        print('No duplicates')
    else:
        print(len(set([x for x in all_times if all_times.count(x) > 1])), 'Duplicates')
        print(set([x for x in all_times if all_times.count(x) > 1]))

    # dodgy files dealing with skipping times still for some reason appending the string name to string list. So here,
    # I am being lazy and manually removing any lists with time length 0 before plotting
    for wind, dir, windall, dirall, time in zip(key_name_winds, key_name_dirs,
                                                key_name_winds_9, key_name_dirs_9,
                                                key_name_times
                                                ):

        if len(time_dict[time][:hoursbeforerepeat]) == 0:
            print('There was a time list which has length 0: ', time)

            key_name_winds.remove(wind)
            key_name_winds_9.remove(windall)
            key_name_dirs.remove(dir)
            key_name_dirs_9.remove(dirall)
            key_name_times.remove(time)

            # not sure I need these:
            del time_dict[time]
            del wind_dict[wind]
            del wind_dict_9[windall]
            del dir_dict[dir]
            del dir_dict_9[dirall]

    # plotting the differences between 3x3 averaged and centre grid
    plt.figure(figsize=(20, 15))

    ax1 = pyplot.subplot(2, 1, 1)
    ax2 = pyplot.subplot(2, 1, 2)

    mod_colour = look_up.model_options[model][1]

    # for wind, time, direction in zip(key_name_winds_9, key_name_times, key_name_dirs_9):
    #     if len(wind_dict_9[wind]) > 0:
    #         plotCollection(ax1, time_dict[time][:], wind_dict_9[wind][0][:],
    #                        'g')
    #
    #         plotCollection(ax2, time_dict[time][:],
    #                        dir_dict_9[direction][0][:],
    #                        'g', label="3x3 averaged %s @ %d m" % (model, height_value))

    for wind, time, direction in zip(key_name_winds, key_name_times, key_name_dirs):
        if len(wind_dict[wind]) > 0:
            plotCollection(ax1, time_dict[time][:], wind_dict[wind][:],
                           mod_colour)
            plotCollection(ax2, time_dict[time][:], dir_dict[direction][:],
                           mod_colour, label="%s @ %d m" % (model, height_value))

    # Try here because if one stash code is missing, plot can't be made (I think)
    # throws an error because 0 is not a date
    try:
        ax2.set_xlabel('DOY')
        ax1.set_ylabel(label_string[0])
        ax2.set_ylabel(label_string[1])
        ax2.xaxis.set_major_formatter(DateFormatter('%j'))

        date_for_title = 'DOY ' + str(DOYstart) + ' - ' + str(DOYstop)
        plt.title(sitechoice + ': ' + date_for_title)

        plt.gcf().autofmt_xdate()

        pylab.savefig(savestring + str(variable) + '_' + str(model) + '_' + sitechoice + '_' +
                      str(DOYstart) + '_' + str(DOYstop) + '.png', bbox_inches='tight')

        plt.close('all')

    except:
        print('WIND PLOTS NOT MADE!!!')
        height_value = 0
        height_value_0 = 0
        height_value_2 = 0

    return (time_dict,
            wind_dict,
            dir_dict,
            key_name_times,
            key_name_winds,
            key_name_dirs,
            height_value,
            all_times,
            key_name_winds_9,
            key_name_dirs_9,
            key_name_winds_0,
            key_name_dirs_0,
            key_name_winds_2,
            key_name_dirs_2,
            height_value_0,
            height_value_2,
            wind_dict_9,
            dir_dict_9,
            wind_dict_0,
            dir_dict_0,
            wind_dict_2,
            dir_dict_2)


def retrieve_arrays_model(included_models, model_grid_choice):
    """
    Return arrays of model data after extract_model_data process
    :param included_models:
    :param model_grid_choice:
    :return:
    """

    try:
        included_model = included_models[model_grid_choice]

        stringtime = included_model[0]
        stringtemp = included_model[1]
        timedict = included_model[2]
        tempdict = included_model[3]

    except KeyError:
        print('No source area included in grid %d' % model_grid_choice)

        stringtime = []
        stringtemp = []
        timedict = []
        tempdict = []

    times = []
    vals = []

    for day in stringtemp:
        for val in tempdict[day]:
            vals.append(val)

    for day in stringtime:
        for time in timedict[day]:
            times.append(time)

    vals_array = np.asarray(vals)
    times_array = np.asarray(times)

    return times_array, vals_array


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
