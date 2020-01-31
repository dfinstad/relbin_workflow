#!/usr/bin/env python

import os
import sys
import h5py
import glob
from subprocess import call

analysis_dir = sys.argv[1]
output_root = "{}/pe".format(analysis_dir)
output_dir = "{}/hdf_inj_files".format(output_root)
if not os.path.exists(output_root):
    os.mkdir(output_root)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
analysis_subdir = glob.glob("{}/analysis*/".format(analysis_dir))[0]
print(analysis_dir)
print(analysis_subdir)
inj_dir = glob.glob("{}/output/BNSSTT2*/".format(analysis_subdir))[0]
injfind_file = glob.glob("{}/*HDFINJFIND*.hdf".format(inj_dir))[0]
injfind = h5py.File(injfind_file, "r")

found_idx = injfind['found_after_vetoes/injection_index'][:]

param_map = {'end_time': 'tc', 'latitude': 'dec', 'longitude': 'ra'}
all_params = ['mass1', 'mass2', 'spin1x', 'spin1y', 'spin1z', 'spin2x',
              'spin2y', 'spin2z', 'coa_phase', 'polarization', 'inclination',
              'end_time', 'latitude', 'longitude', 'distance']
approx = 'SpinTaylorT2'
taper = 'startend'
for idx in found_idx:
    print("Processing injection {}".format(idx))
    # get injection params
    params = {'approximant': approx, 'taper': taper, 'f_lower': 25}
    for p in all_params:
        key = param_map[p] if p in param_map else p
        params[key] = injfind['injections/{}'.format(p)][idx]

    # write injection config file
    config_str = "[variable_params]\n\n[static_params]\n"
    for k, v in params.items():
        config_str += "{} = {}\n".format(k, v)
    with open("{}/inj_config_temp.ini".format(output_dir), "w") as fp:
        fp.write(config_str)

    # create injection from config
    cmd_str = "pycbc_create_injections --verbose --ninjections 1 "
    cmd_str += "--config-file {}/inj_config_temp.ini ".format(output_dir)
    cmd_str += "--output-file {}/injection_{}.hdf".format(output_dir, idx)
    call([cmd_str], shell=True)

injfind.close()

print("Done")
