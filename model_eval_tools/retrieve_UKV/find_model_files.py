import os.path
import datetime as dt
from calendar import isleap
import sys

from scint_eval import look_up


def find_UKV_files(DOYstart,
                   DOYstop,
                   sitechoice,
                   model_name,
                   run,
                   variable,
                   model_path="/storage/basic/micromet/Tier_processing/rv006011/new_data_storage/"):
    """
    :param DOYstart:
    :param DOYstop:
    :param sitechoice:
    :param model_name: String. What model are files being found for? Can either be 'ukv' or 'lon'
    :param run: what model run: should be a string, '06Z' or '21Z'.
    :param variable:
    :param model_path:
    :return:
    """

    # make sure that the model request given is an option.
    assert model_name in look_up.model_options.keys()

    # finding start and stop years, and start and stop DOYs
    # (has been re-done to include the option to run more than one year at once)
    # makes into string
    strDOYstart = str(DOYstart)
    strDOYstop = str(DOYstop)
    # splits sting, year (first 4 digits of string):
    start_year = strDOYstart[:4]
    stop_year = strDOYstop[:4]
    # DOY (last 3 digits of string)
    start_DOY = strDOYstart[4:]
    stop_DOY = strDOYstop[4:]

    # finding number of years we are dealing with:
    num_of_years = int(stop_year) - int(start_year) + 1  # the + 1 is included to represent the actual number of years
    # creates a list for all years included
    year_list = []
    if num_of_years == 1:
        year_list.append(start_year)
    elif num_of_years == 2:
        year_list.append(start_year)
        year_list.append(stop_year)
    else:
        for i in range(0, num_of_years):
            year_to_append = int(start_year) + i
            year_list.append(str(year_to_append))

    # DOY dictionary (used to be list) for all DOYs in between start and stop (the ones we want), for each year included
    DOYlist = {}
    # creates each year included as a key
    for item in year_list:
        DOYlist[item] = []

    # fills dictionary based on DOYs available in that year
    # wraps the string to be zero padded.
    # if only 1 year is avalible
    if num_of_years == 1:
        for item in range(int(start_DOY), int(stop_DOY) + 1):
            if item < 10:
                DOYlist[start_year].append('00' + str(item))
            if item < 100:
                if item > 9:
                    DOYlist[start_year].append('0' + str(item))
            else:
                DOYlist[start_year].append(str(item))

    # if 2 years are chosen
    elif num_of_years >= 2:
        # is the first year a leap year?
        if isleap(int(start_year)):
            whole_year = 367
        else:
            whole_year = 366
        # fills the first year
        for item in range(int(start_DOY), whole_year):
            if item < 10:
                DOYlist[start_year].append('00' + str(item))
            if item < 100:
                if item > 9:
                    DOYlist[start_year].append('0' + str(item))
            else:
                DOYlist[start_year].append(str(item))
        # fills the last year
        for item in range(1, int(stop_DOY) + 1):
            if item < 10:
                DOYlist[stop_year].append('00' + str(item))
            if item < 100:
                if item > 9:
                    DOYlist[stop_year].append('0' + str(item))
            else:
                DOYlist[stop_year].append(str(item))
        # fills any years in-between (if there are any)
        if num_of_years > 2:
            for year in year_list[1:-1]:
                # is this year a leap year?
                if isleap(int(year)):
                    whole_year = 367
                else:
                    whole_year = 366
                # fills the year
                for item in range(1, whole_year):
                    if item < 10:
                        DOYlist[year].append('00' + str(item))
                    if item < 100:
                        if item > 9:
                            DOYlist[year].append('0' + str(item))
                    else:
                        DOYlist[year].append(str(item))

    # prints out DOYs chosen in terminal
    print('DOYs chosen:')
    for key in sorted(DOYlist.keys()):
        print('year:', key)
        print(DOYlist[key])

    # creates dictionaries to append model files to
    ukvdict = {}

    # finding model files year by year.
    for year in year_list:
        print(' ')
        print('For year: ', year)
        # finding all model DOYs which exists
        modmainpath = model_path + year + '/London/L2/MetOffice/DAY'
        DOYoptionsmod = os.listdir(modmainpath)
        # List of all matches between avalible DOYs and wanted DOYs
        DOYmatchesmod = []
        for item in DOYoptionsmod:
            if item in DOYlist[year]:
                DOYmatchesmod.append(item)
        modmissingDOY = []
        if len(DOYmatchesmod) == len(DOYlist[year]):
            print('All model DOYs found')
        else:
            print('There is a missing DOY/DOYs for the model:')
            for item in DOYlist[year]:
                if item in DOYmatchesmod:
                    pass
                else:
                    print(item)
                    modmissingDOY.append(item)

        ukvfilepaths = []
        for item in DOYmatchesmod:

            # (Changed to see if I can get more relevant missing files to work)
            if variable == 'wind' or variable == 'RH_q' or variable == 'kup':
                # requires more than one stash code.
                codes = look_up.variables[variable]
                dateobject = dt.datetime.strptime(str(year) + ' ' + item, '%Y %j')
                for code in codes:
                    # where model_options[model_name][0] is the model filename preface
                    filename = look_up.model_options[model_name][0] + dateobject.strftime(
                        '%Y%m%d') + run + '_' + code + '_' + look_up.sites[
                                   sitechoice] + '.nc'

                    pathto = modmainpath + '/' + item + '/'
                    path = pathto + filename
                    ukvfilepaths.append(path)

            else:
                # requires only one stash code
                code = look_up.variables[variable]
                dateobject = dt.datetime.strptime(str(year) + ' ' + item, '%Y %j')

                # where model_options[model_name][0] is the model filename preface
                filename = look_up.model_options[model_name][0] + dateobject.strftime(
                    '%Y%m%d') + run + '_' + code + '_' + look_up.sites[
                               sitechoice] + '.nc'

                pathto = modmainpath + '/' + item + '/'
                path = pathto + filename
                ukvfilepaths.append(path)

        # Changed to see if I can get more relevant missing files to work
        ukvexist = 0
        ukvexistlist = []
        ukvdontexistlist = []
        for item in ukvfilepaths:
            if os.path.exists(item) == True:
                ukvexist += 1
                ukvexistlist.append(item)
            else:
                ukvdontexistlist.append(item)

        if len(ukvdontexistlist) == 0:
            print('all ' + str(len(ukvexistlist)) + ' files exist from ' + str(len(DOYlist[year])) + ' DOYs')
        else:
            totalleng = len(ukvexistlist) + len(ukvdontexistlist)
            print(str(ukvexist) + ' out of ' + str(totalleng) + ' files found. Missing:')
            ukvmissinglist = modmissingDOY + ukvdontexistlist
            print(ukvmissinglist)

        ukvDOYs = []
        for item in ukvexistlist:

            # KSSW is a site with more letters than others, so it's handled differently when finding the date:
            if sitechoice == 'KSSW':
                strip = item[-34:-26]
            elif sitechoice == 'BFCL':
                strip = item[-34:-26]
            elif sitechoice == 'MR':
                strip = item[-32:-24]
            elif sitechoice == 'NK':
                strip = item[-32:-24]
            else:
                strip = item[-33:-25]
            time = dt.datetime.strptime(strip, '%Y%m%d')
            DOY = time.strftime('%j')
            ukvDOYs.append(DOY)

        # Making a list of the index where the DOY changes
        doychangeukv = []
        for i in range(1, len(ukvDOYs)):
            if ukvDOYs[i - 1] == ukvDOYs[i]:
                pass
            else:
                doychangeukv.append(i)

        if len(doychangeukv) == 0:
            if len(ukvDOYs) == 0:
                print('No files for: ' + model_name)
            else:
                ukvlistdoy0 = ukvDOYs
                ukvlist0 = ukvexistlist
                ukvdict[model_name + year + str(ukvlistdoy0[0])] = ukvlist0

        else:
            # Creating a dictionary for the values of each DOY
            # first item
            ukvlistdoy0 = ukvDOYs[0:doychangeukv[0]]
            ukvlist0 = ukvexistlist[0:doychangeukv[0]]
            ukvdict[model_name + year + str(ukvlistdoy0[0])] = ukvlist0

            # middle items
            ukvi = 1
            for item in range(1, len(doychangeukv)):
                listdoy = ukvDOYs[doychangeukv[ukvi - 1]:doychangeukv[ukvi]]
                list = ukvexistlist[doychangeukv[ukvi - 1]:doychangeukv[ukvi]]
                ukvdict[model_name + year + str(listdoy[0])] = list
                ukvi += 1

            # final item
            ukvlistdoyend = ukvDOYs[doychangeukv[-1]:len(ukvDOYs)]
            ukvlistend = ukvexistlist[doychangeukv[-1]:len(ukvexistlist)]
            ukvdict[model_name + year + str(ukvlistdoyend[0])] = ukvlistend

    print(' ')
    return ukvdict


def order_model_stashes(files,
                        variable):
    """
    Sorts model files after they've been found - needs to be done as some variables require more than one stash code.
    Also needs to be done for variables with one stash code - as file paths are produced as lists from the other
    finding files function at the moment. This in the future could be moved to the other function (like how the obs
    have been handled).
    :param files:
    :param variable:
    :return:
    """

    print(' ')
    print('-----------------------------------------------------------------------------------------------------------')
    print('Ordering Model files: ')
    print(' ')

    # finds the stash code of the variable I am looking at
    stash = look_up.variables[variable]
    # if there is more than one stash code involved in this variable:
    if type(stash) == list:
        print('Variable: ', variable, ' uses more than one stash code.')

        if variable == 'RH_q':
            RH_stash = look_up.variables[variable]
            T_stash = RH_stash[0]
            P_stash = RH_stash[1]
            Q_stash = RH_stash[2]

            new_ukv_T = {}
            new_ukv_P = {}
            new_ukv_Q = {}

            # T
            for key in files.keys():
                for item in files[key]:
                    if T_stash in item:
                        new_ukv_T[key] = item
            # P
            for key in files.keys():
                for item in files[key]:
                    if P_stash in item:
                        new_ukv_P[key] = item
            # Q
            for key in files.keys():
                for item in files[key]:
                    if Q_stash in item:
                        new_ukv_Q[key] = item

            list_to_return = [new_ukv_T, new_ukv_P, new_ukv_Q]
            return list_to_return

        elif variable == 'wind':
            wind_stash = look_up.variables[variable]
            u_stash = wind_stash[0]
            v_stash = wind_stash[1]

            new_ukv_u = {}
            new_ukv_v = {}

            # u
            for key in files.keys():
                for item in files[key]:
                    if u_stash in item:
                        new_ukv_u[key] = item
            # v
            for key in files.keys():
                for item in files[key]:
                    if v_stash in item:
                        new_ukv_v[key] = item

            list_to_return = [new_ukv_u, new_ukv_v]
            return list_to_return

        elif variable == 'kup':
            up_stash = look_up.variables[variable]
            down_stash = up_stash[0]
            star_stash = up_stash[1]

            new_ukv_down = {}
            new_ukv_star = {}

            for key in files.keys():
                for item in files[key]:
                    if down_stash in item:
                        new_ukv_down[key] = item

            for key in files.keys():
                for item in files[key]:
                    if star_stash in item:
                        new_ukv_star[key] = item

            # making sure both stash codes needed have the same amount of files
            for down_item in new_ukv_down.keys():
                if down_item in new_ukv_star:
                    pass
                else:
                    del new_ukv_down[down_item]
            for star_item in new_ukv_star.keys():
                if star_item in new_ukv_down:
                    pass
                else:
                    del new_ukv_star[star_item]
            # Test if the keys are now the same
            if sorted(new_ukv_star.keys()) == sorted(new_ukv_down.keys()):
                if len(new_ukv_down) == len(new_ukv_star):
                    pass
            else:
                print("ERROR: The keys between both stash codes are different")
                sys.exit()

            list_to_return = [new_ukv_down, new_ukv_star]
            return list_to_return

    # for variables which only use one stash code:
    else:
        # define a dictionary
        new_model = {}
        for key in files.keys():
            for item in files[key]:
                if stash in item:
                    new_model[key] = item
        return new_model
