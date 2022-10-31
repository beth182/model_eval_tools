# z0 and zd calculated in UMEP, using the McDonald 1998 method, and using a source area of 500 m.
obs_z0_macdonald = {'BCT': 1.664,
                    'BFCL': 1.368,
                    'BGH': 1.436,
                    'BTT': 1.147,
                    'IML': 0.862,
                    'IMU': 0.887,
                    'KSSW': 1.811,
                    'MR': 1.208,
                    'NK': 1.001,
                    'RGS': 2.084,
                    'SWT': 1.073}

obs_zd_macdonald = {'BCT': 16.874,
                    'BFCL': 16.376,
                    'BGH': 18.966,
                    'BTT': 13.759,
                    'IML': 9.386,
                    'IMU': 9.367,
                    'KSSW': 13.238,
                    'MR': 9.783,
                    'NK': 5.321,
                    'RGS': 8.821,
                    'SWT': 5.584}

# Dictionary for positions of site grids relative to each other
# This one is only correct for STASH CODES (not lancover data)
grid_dict = {1: ['MR A', 'BTT A'],
             2: ['MR B', 'BTT B'],
             3: ['MR C', 'BTT C', 'IMU A', 'IML A'],
             4: ['IMU B', 'IML B', 'BFCL A', 'BCT A'],
             5: ['IMU C', 'IML C', 'BFCL B', 'BCT B'],
             6: ['BFCL C', 'BCT C'],
             7: ['NK A'],
             8: ['NK B'],
             9: ['NK C'],
             10: ['MR D', 'BTT D'],
             11: ['MR E', 'BTT E', 'KSSW A'],
             12: ['MR F', 'BTT F', 'IMU D', 'IML D', 'KSSW B'],
             13: ['IMU E', 'IML E', 'BFCL D', 'BCT D', 'BGH A', 'KSSW C'],
             14: ['IMU F', 'IML F', 'BFCL E', 'BCT E', 'BGH B'],
             15: ['BFCL F', 'BCT F', 'BGH C'],
             16: ['NK D'],
             17: ['NK E'],
             18: ['RGS A', 'NK F'],
             19: ['MR G', 'BTT G', 'RGS B'],
             20: ['MR H', 'BTT H', 'RGS C', 'KSSW D'],
             21: ['MR I', 'BTT I', 'IMU G', 'IML G', 'KSSW E'],
             22: ['IMU H', 'IML H', 'BFCL G', 'BCT G', 'BGH D', 'KSSW F'],
             23: ['IMU I', 'IML I', 'BFCL H', 'BCT H', 'BGH E'],
             24: ['BFCL I', 'BCT I', 'BGH F'],
             25: ['NK G'],
             26: ['NK H'],
             27: ['RGS D', 'NK I'],
             28: ['RGS E'],
             29: ['RGS F', 'KSSW G'],
             30: ['KSSW H'],
             31: ['BGH G', 'KSSW I', 'SWT A'],
             32: ['BGH H', 'SWT B'],
             33: ['BGH I', 'SWT C'],
             34: ['RGS G'],
             35: ['RGS H'],
             36: ['RGS I'],
             37: ['SWT D'],
             38: ['SWT E'],
             39: ['SWT F'],
             40: ['SWT G'],
             41: ['SWT H'],
             42: ['SWT I']
             }

# This one is only correct fro landuse fractions (not stash codes) - KSSW shifts
grid_dict_lc = {1: ['MR A', 'BTT A'],
             2: ['MR B', 'BTT B'],
             3: ['MR C', 'BTT C', 'IMU A', 'IML A'],
             4: ['IMU B', 'IML B', 'BFCL A', 'BCT A'],
             5: ['IMU C', 'IML C', 'BFCL B', 'BCT B'],
             6: ['BFCL C', 'BCT C'],
             7: ['NK A'],
             8: ['NK B'],
             9: ['NK C'],
             10: ['MR D', 'BTT D'],
             11: ['MR E', 'BTT E'],
             12: ['MR F', 'BTT F', 'IMU D', 'IML D', 'KSSW A'],
             13: ['IMU E', 'IML E', 'BFCL D', 'BCT D', 'BGH A', 'KSSW B'],
             14: ['IMU F', 'IML F', 'BFCL E', 'BCT E', 'BGH B', 'KSSW C'],
             15: ['BFCL F', 'BCT F', 'BGH C'],
             16: ['NK D'],
             17: ['NK E'],
             18: ['RGS A', 'NK F'],
             19: ['MR G', 'BTT G', 'RGS B'],
             20: ['MR H', 'BTT H', 'RGS C'],
             21: ['MR I', 'BTT I', 'IMU G', 'IML G', 'KSSW D'],
             22: ['IMU H', 'IML H', 'BFCL G', 'BCT G', 'BGH D', 'KSSW E'],
             23: ['IMU I', 'IML I', 'BFCL H', 'BCT H', 'BGH E', 'KSSW F'],
             24: ['BFCL I', 'BCT I', 'BGH F'],
             25: ['NK G'],
             26: ['NK H'],
             27: ['RGS D', 'NK I'],
             28: ['RGS E'],
             29: ['RGS F'],
             30: ['KSSW G'],
             31: ['BGH G', 'SWT A', 'KSSW H'],
             32: ['BGH H', 'SWT B', 'KSSW I'],
             33: ['BGH I', 'SWT C'],
             34: ['RGS G'],
             35: ['RGS H'],
             36: ['RGS I'],
             37: ['SWT D'],
             38: ['SWT E'],
             39: ['SWT F'],
             40: ['SWT G'],
             41: ['SWT H'],
             42: ['SWT I']
             }

# dict to help with adding new variables to Model Eval
# still will have to make edits to sort_obs and sort_models when adding a new variable
# order is:
# 1. label for plot axis (variable name and unit as string) -- wind has two for speed and direction (in that order)
# 2. either 'levels' or 'surface', dependant on if the variable is at the surface or on model levels. This is to help
# for the legend in time series plots
# 3. unit string only (used within moving stats)
# 4. hit rate thresholds as a list, [harsh, kind]
# 5. Histogram bin size
# 6. y limit for the ensemble metrics
variable_info = {'Tair': ['Air Temperature ($^{\circ}$C)', 'levels', '$^{\circ}$C', [0.5, 1.0], 0.5, [0, 25]],
                 'RH': ['Relative Humidity (%)', 'levels', '%', [1.0, 5.0], 2.0, []],
                 'RH_q': ['Relative Humidity (%)', 'levels', '%', [1.0, 5.0], 2.0, [0, 100]],
                 'Press': ['Pressure (hPa)', 'levels', 'hPa', [1.0, 2.25], 2.0, []],
                 'wind': [['Wind Speed (m s$^{-1}$)', 'Wind Direction ($^{\circ}$)'], 'levels', 'm s$^{-1}$',
                          [0.5, 1.0], 2.0, []],
                 'kdown': ['Incoming Shortwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 10,
                           [0, 400]],
                 'ldown': ['Incoming Longwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],
                 'lstar': ['Net Longwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],
                 'lup': ['Outgoing Longwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],
                 'kup': ['Outgoing Shortwave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],
                 'netallwave': ['Net All-Wave Radiation (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [0.5, 1.0], 2.0, []],
                 'H': ['Sensible Heat Flux (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [25, 80], 10, [-50, 300]],
                 'LE': ['Latent Heat Flux (W m$^{-2}$)', 'surface', 'W m$^{-2}$', [5, 20], 10, [-10, 50]],
                 'CT2': ['CT2'],  # Added for scintillometry eval
                 'X_c': ['X_c'],  # Added for scintillometry eval
                 'Y_c': ['Y_c'],  # Added for scintillometry eval
                 'X_c, Y_c': ['X_c, Y_c'],  # Added for scintillometry eval
                 'sd_v': ['sd_v'],  # Added for scintillometry eval
                 'L': ['L'],  # Added for scintillometry eval
                 'ustar': ['ustar'],  # Added for scintillometry eval
                 'PAR_W': ['PAR'],  # Added for kdown allignment tests
                 'BL_H': ['BL Heat Flux (W m$^{-2}$)', 'levels', 'W m$^{-2}$', [25, 80], 10, [-50, 300]]}

# for MODEL files
premade_model_site_codes = {'Heathrow': 'Heathrow',
                            'BCT': 'LON_BCT',
                            'BFCL': 'LON_BFCL',
                            'BGH': 'LON_BGH',
                            'BTT': 'LON_BTT',
                            'IML': 'LON_IML',
                            'IMU': 'LON_IMU',
                            'KSSW': 'LON_KSSW',
                            'MR': 'LON_MR',
                            'NK': 'LON_NK',
                            'RGS': 'LON_RGS',
                            'SWT': 'LON_SWT',
                            'Reading': 'Reading'}


# calculated from notebooks/surface_altitudes/lon_ukv_surface_altitudes.ipynb
# stash m01s00i033
UKV_site_altitudes = {'Heathrow': 26.084702,
                      'LON_BCT': 25.500525,
                      'LON_BFCL': 25.500525,
                      'LON_BGH': 17.123268,
                      'LON_BTT': 43.288658,
                      'LON_IML': 29.193649,
                      'LON_IMU': 29.193649,
                      'LON_KSSW': 26.755775,
                      'LON_MR': 43.288658,
                      'LON_NK': 28.70874,
                      'LON_RGS': 19.805748,
                      'LON_SWT': 3.0381837,
                      'Reading': 43.790215}

LON_site_altitudes = {'Heathrow': 22.805416107177734,
                      'LON_BCT': 28.072063446044922,
                      'LON_BFCL': 29.131160736083984,
                      'LON_BGH': 29.131160736083984,
                      'LON_BTT': 35.290924072265625,
                      'LON_IML': 24.953636169433594,
                      'LON_IMU': 24.953636169433594,
                      'LON_KSSW': 17.655845642089844,
                      'LON_MR': 35.698440551757813,
                      'LON_NK': 25.287059783935547,
                      'LON_RGS': 26.907081604003906,
                      'LON_SWT': 6.5159897804260254,
                      'Reading': 62.51922607421875}


# models that are avalible and their settings
# 0 - file name preface
# 1 - model colour for plotting
# 2 - z0_index
model_options = {'ukv': ['MOUKV_FC', 'b', 0],
                 'lon': ['MOLON_FC', 'r', 1],
                 'mor': ['MOMOR_FC', 'purple', 1]}

# for finding files: stash codes
# kup: down then star
# wind: u then v
variables = {'Tair': 'm01s16i004',
             'RH': 'm01s09i229',
             'Press': 'm01s00i408',
             'wind': ['m01s00i002', 'm01s00i003'],
             'kdown': 'm01s01i235',
             'ldown': 'm01s02i207',
             'kup': ['m01s01i235', 'm01s01i201'],
             'lstar': 'm01s02i201',
             'RH_q': ['m01s16i004', 'm01s00i408', 'm01s00i010'],
             'H': 'm01s03i217',
             'LE': 'm01s03i234',
             'BL_H': 'm01s03i216',
             'z0': 'm01s03i026'}
