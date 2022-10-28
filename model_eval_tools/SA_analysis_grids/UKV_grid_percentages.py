from model_eval_tools import look_up


def determine_which_model_files(model_site_dict,
                                DOYstart_mod,
                                DOYstop_mod,
                                run,
                                instrument,
                                sample,
                                variable,
                                obs_level,
                                model_format,
                                disheight,
                                z0zdlist,
                                saveyn,
                                savepath):
    """
    finds all the grids which will be needed - looks through the whole model site dict and gets all grid numbers
    across whole time range chosen
    """

    # list which will include all grid numbers
    # made as a set to avoid repeats
    all_items_set = set([])

    for hour in model_site_dict:
        for grid_num in model_site_dict[hour]:
            all_items_set.add(grid_num)

    model_site_for_sort = []
    for grid in sorted(list(all_items_set)):
        model_site_for_sort.append(int(grid))

    model_site_sorted = sorted(model_site_for_sort)

    model_site = []
    for item in model_site_sorted:
        model_site.append(str(item))

    # dictionary to append model data to, for all sites chosen.
    included_grids = {}

    # for every grid chosen & present in list:
    for grid in model_site:
        print(' ')
        print(' ')
        print(
            '---------------------------------------------------------------------------------------------------')
        print(' ')
        print('GRID NUMBER CHOSEN: ', grid)

        # changes to int
        grid = int(grid)

        # For this grid:

        # calling grid_dict from variables.py to see what sites include this grid as part of their 3x3
        print('Options with this grid number are: ', look_up.grid_dict[grid])

        # Step 1:
        # makes lists for sites and grid litters for all items called from variables.py,
        # in order to find files for them (based on what is present in the grid_dict)

        # list of sites
        sites_present = []
        # list of corresponding grid letters
        grid_letters = []

        # for each site which includes the chosen grid
        for item in look_up.grid_dict[grid]:
            # split the items present in the dict to get a site name and a grid letter
            site_present = item.split(' ')[0]
            grid_letter = item.split(' ')[1]

            # append them to the lists above
            sites_present.append(site_present)
            grid_letters.append(grid_letter)

        # Step 2:
        # finds files for all sites containing the current grid choice

        # list to append found file dicts to
        dict_list = []
        # list to append the keys of the found file dicts to
        # keys are strings of like, model type and date
        key_list = []

        # for every site which includes our grid in it's 3x3
        for sitei in sites_present:
            # finds the files for the site
            print(' ')

            print(' ')
            print('FINDING FILES FOR SITE: ', sitei)
            file_dict_ukv = file_read.finding_files(model_format,
                                                    'ukv',
                                                    DOYstart_mod,
                                                    DOYstop_mod,
                                                    sitei,
                                                    run,
                                                    instrument,
                                                    sample,
                                                    variable,
                                                    obs_level,
                                                    # model_path="//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_storage/"
                                                    model_path='C:/Users/beths/Desktop/LANDING/data_wifi_problems/data/'
                                                    )

            # append the keys to key_list
            list_of_keys = file_dict_ukv.keys()
            key_list.append(list_of_keys)

        # append the dictionaries to dict_list
        dict_list.append(file_dict_ukv)

        # Step 3: Put together a collection of unique files found for each day chosen, for this grid.
        # This maximises the data availability for the model -
        # As one site (example, IMU) may have it's grid A matching with our chosen grid, and another site (BCT)
        # may have it's grid E also matching, but files are available for IMU which aren't for BCT...

        # Takes the key_list, which is a list of lists (list of lists of keys for all sites' files found)
        # and then finds all the unique items (gets rid of keys which appear more than once throughout all the
        # sites
        unique_keys = list(set(x for l in key_list for x in l))

        # Creates a dictionary to keep a collection of as-complete-as-possible files found for this grid
        complete_files = {}

        # for each unique key
        for item in unique_keys:

            # for dicts in list of dicts (one for each site)
            for dict in dict_list:

                # if the unique key is in this dict
                if item in dict:

                    # define unique item in new dict
                    complete_files[item] = dict[item]

                    # and then this item has been found, so no longer need to look for this unique key
                    # break the loop here
                    break

                # if the item was not in this dict, keep looking
                else:
                    pass

        # Step 4: Find the corresponding sites and grid letters which this new collection of unique file items
        # correspond to

        # Finding the site string for each site used in the unique collection
        # defines a list of sites used
        sites_used = []

        # for every item in the unique file collection
        for item in sorted(complete_files):
            # get the site which corresponds to this key
            # split by underscore, get the last item: example KSSW.nc, use [:-3] to get rid of .nc
            site_here = complete_files[item][0].split('_')[-1][:-3]

            # append to list of sites used
            sites_used.append(site_here)

        # Finding the grid letter for each site used in the unique collection
        # defines a list of letters used
        grid_letters_used = []

        # for every site used
        for item in sites_used:
            # find where this appears in sites present, and from that, can get the letter
            letter = np.asarray(grid_letters)[np.where(np.asarray(sites_present) == item)][0]

            # append to list
            grid_letters_used.append(letter)

        # Step 5: Finding where site changes occur
        # eventually will contribute to splitting up the complete dictionary up into chunks of the same site.
        # This is because the sort_models function can only take one site/ grid letter at once.

        # define list of indexes where site changes within the sites_used list
        # (sites_used being a list of sites included within the complete collection)
        site_change = []
        # for the index between 0 and the length of the complete collection
        for i in range(0, len(sites_used)):

            # if it is not the first index
            if i != 0:

                # if the current site is not the same as the previous site, there is a site change and the index (i)
                # is appended
                if sites_used[i] != sites_used[i - 1]:
                    site_change.append(i)

        # if there are no changes, the site change list == []
        # so need to append a 0 to get first and only site used
        if len(site_change) == 0:
            site_change.append(0)

        # Step 6: Splits up the complete dictionary KEYS up into chunks of the same site.

        # creating a list of lists
        # This will be be lists of keys from the complete collection - separated by differing sites used
        list_of_lists = []

        # if the length of the site changes is more than one
        # meaning more than one site is included here
        if len(site_change) != 1:

            # Defining the first list (for the first site)
            # append all keys until the first index change
            list_of_lists.append(sorted(complete_files.keys())[:site_change[0]])

            # Defining all the middle lists
            # makes list of tuples of 2 indices to slice by
            indices_tuple = []
            # for all indices in between the first and last
            for i in range(1, len(site_change)):
                # defines pair of indicies to slice by (in form of tuple)
                tuple = site_change[i - 1], site_change[i]
                # appends
                indices_tuple.append(tuple)
            # slice list by these tuples
            for item in [sorted(complete_files.keys())[s:e] for s, e in indices_tuple]:
                # append to list of lists
                list_of_lists.append(item)

            # Defining the last list
            # append all the keys from the last index change to the end of the complete keys
            list_of_lists.append(sorted(complete_files.keys())[site_change[-1]:])

        # If only one site is included
        else:
            list_of_lists.append(sorted(complete_files.keys())[site_change[-1]:])

        # Step 7: Splits up the complete dictionary (no longer just keys, but values too)
        # up into chunks of the same site.

        # creates list to append dictionaries to (one for each site used in chunks)
        list_of_dicts = []

        # for every list in list of lists, or, for every chunk of consecutive sites used in complete collection:
        for listi in list_of_lists:
            # define a dictionary
            temp_dict = {}
            # for every item (which is a key in the complete collection) in this current list
            for item in listi:
                # defines an item in the new dictionary, by calling the item from the original dictionary
                temp_dict[item] = complete_files[item]
            # append this temporary dictionary to my list of dictionaries.
            list_of_dicts.append(temp_dict)

        # Step 8: Gets a list of sites and grid letters - one for each dictionary of files for
        # each site (one for each cluster)

        # Creates lists of sites and grid letters which the list of dicts correspond to
        # so one site and grid letter per dictionary of files

        # defines lists of sites and grid letters
        list_of_sites_for_final = []
        list_of_grids_for_final = []

        # append the first item
        list_of_sites_for_final.append(sites_used[0])
        list_of_grids_for_final.append(grid_letters_used[0])

        # appends the further items, using list of indicies where changes occured
        for item in site_change:
            list_of_sites_for_final.append(sites_used[item])
            list_of_grids_for_final.append(grid_letters_used[item])

        # Step 9: Defines empty lists for the output of sort_models to be appended to.

        # dict of datetimes
        # lontimedict
        combined_ukv0_list = []
        # dict of temps
        # lontempdict
        combined_ukv1_list = []
        # dict of temp 9
        # lontempdict9
        combined_ukv2_list = []
        # dict of temp 0
        # lontempdict0
        combined_ukv3_list = []
        # dict of temp 2
        # lontempdict2
        combined_ukv4_list = []
        # list of strings time
        # stringtimelon
        combined_ukv5_list = []
        # list of strings temp
        # stringtemplon
        combined_ukv6_list = []
        # list of strings temp9
        # stringtemplon9
        combined_ukv7_list = []
        # list of strings temp 0
        # stringtemplon0
        combined_ukv8_list = []
        # list of strings temp2
        # stringtemplon2
        combined_ukv9_list = []

        # ToDo: I REALLY NEED TO CHANGE THIS!
        # Heights atm are changing with grid because of the sites are different - so I need to change this
        # This will be the case when a stash code is used which ISN'T from the surface

        # height of model
        # modheightvaluelon
        combined_ukv10_list = []
        # height of model0
        # modheightvaluelon0
        combined_ukv11_list = []
        # height of model2
        # modheightvaluelon2
        combined_ukv12_list = []
        # alllontimes
        combined_ukv13_list = []

        # Step 10: Runs sort models for each cluster of files, and appends output.

        for file_dict_ukv, site_item, grid_item in zip(list_of_dicts, list_of_sites_for_final,
                                                       list_of_grids_for_final):
            # pulls the start and stop DOY for this cluster from the dictionary key
            DOYstart_temp = int(list(file_dict_ukv.keys())[0][3:])
            DOYstop_temp = int(list(file_dict_ukv.keys())[-1][3:])

            # ordering UKV model files
            # file_read.py
            files_ukv = file_read.order_model_stashes('ukv', file_dict_ukv, variable)

            # sort models
            # models.py
            ukv = sort_model.sort_models(variable, 'ukv', files_ukv, disheight, DOYstart_temp, DOYstop_temp,
                                         site_item, savepath, model_format, grid_item)

            # appends outputs to lists
            combined_ukv0_list.append(ukv[0])
            combined_ukv1_list.append(ukv[1])
            combined_ukv2_list.append(ukv[2])
            combined_ukv3_list.append(ukv[3])
            combined_ukv4_list.append(ukv[4])
            combined_ukv5_list.append(ukv[5])
            combined_ukv6_list.append(ukv[6])
            combined_ukv7_list.append(ukv[7])
            combined_ukv8_list.append(ukv[8])
            combined_ukv9_list.append(ukv[9])
            combined_ukv10_list.append(ukv[10])
            combined_ukv11_list.append(ukv[11])
            combined_ukv12_list.append(ukv[12])
            combined_ukv13_list.append(ukv[13])

        # Step 11: Combines outputs into one item for each output

        # combines dictionaries
        combined_ukv0 = {}
        for d in combined_ukv0_list:
            combined_ukv0.update(d)
        combined_ukv1 = {}
        for d in combined_ukv1_list:
            combined_ukv1.update(d)
        combined_ukv2 = {}
        for d in combined_ukv2_list:
            combined_ukv2.update(d)
        combined_ukv3 = {}
        for d in combined_ukv3_list:
            combined_ukv3.update(d)
        combined_ukv4 = {}
        for d in combined_ukv4_list:
            combined_ukv4.update(d)

        # combines lists
        combined_ukv5 = sum(combined_ukv5_list, [])
        combined_ukv6 = sum(combined_ukv6_list, [])
        combined_ukv7 = sum(combined_ukv7_list, [])
        combined_ukv8 = sum(combined_ukv8_list, [])
        combined_ukv9 = sum(combined_ukv9_list, [])
        combined_ukv13 = sum(combined_ukv13_list, [])

        # takes the height (currently botched)
        # ToDo: edit this - as multiple sites will have more than one height
        temp_height_botch = combined_ukv10_list[0]

        # Step 12: Appends the outputs into the included_grids dictionary (one grouped output per grid)
        # This then acts as 'included_models'

        # groups the outputs for the time series plots
        # [ stringtimelon,  stringtemplon,  lontimedict,    lontempdict,    modheightvaluelon   ]
        group_ukv = [combined_ukv5, combined_ukv6, combined_ukv0, combined_ukv1, temp_height_botch]

        # appends to dictionary
        included_grids[grid] = group_ukv

    return included_grids, model_site
