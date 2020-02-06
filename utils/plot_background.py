#!/usr/bin/env python

import numpy as np
import h5py
from matplotlib import pyplot as plt

sn_model = np.array([
    [8.467102971640177, 9.86624843178948],
    [8.48286861354012, 8.62328052901493],
    [8.750756200846945, 1.0553385749880748],
    [8.993492089680839, 0.14384498882876628],
    [9.179508331958424, 0.03016700280971416],
    [9.368677702615997, 0.00615848211066026],
    [9.557828741131827, 0.0012915496650148853],
    [9.753304368549378, 0.0002498393369881466],
    [9.91723954609617, 0.00006412354795576904],
    [10.018075491759703, 0.000029763514416313192],
    [10.144163962675758, 0.000010696452479219231]])

live_model = np.array([
    [8.611340262882912, 9.348893962206356],
    [8.74993125446846, 3.5457458424656],
    [8.857045958679352, 1.623776739188721],
    [8.901153091715706, 1.1753722651306349],
    [8.961007534510257, 0.7639077845044216],
    [9.027076573356066, 0.5382625345418278],
    [9.096262076298373, 0.3896218237338941],
    [9.140277548626006, 0.3226799119945807],
    [9.165502575665915, 0.26013852794774733],
    [9.19070927056408, 0.21544346900318823],
    [9.228491814698712, 0.169071410347358],
    [9.247447249262132, 0.1363022183003133],
    [9.313461291682707, 0.10412232560483044],
    [9.329300262149626, 0.08171103315457195],
    [9.39214284404847, 0.06587391124079929],
    [9.445617701516069, 0.05032159359259993],
    [9.461667491613046, 0.02897265560913924],
    [9.534015289006215, 0.02014158146560701],
    [9.568974683312252, 0.00999999999999999]
])

cone_lower = np.array([
    [8.14795918367347, 99.10225825398611],
    [9.346938775510203, 0.00994006064217062]])

cone_upper = np.array([
    [8.275510204081634, 100.0000000000001],
    [9.816326530612244, 0.00994006064217062]])

# get search pipeline background
sm_file =
with h5py.File(sm_file, 'r') as fp:
    far = 1./fp['background_exc/ifar'][:]
    stat = fp['background_exc/stat'][:]

sort_idx = np.argsort(stat)

fig, ax = plt.subplots()
ax.plot(cone_lower[:, 0], cone_lower[:, 1], color='k', linestyle='dashed')
ax.plot(cone_upper[:, 0], cone_upper[:, 1], color='k', linestyle='dashed',
        label='approx. pycbc live fig. 2 region')
ax.plot(sn_model[:, 0], sn_model[:, 1], color='C0', label='Signal-Noise model')
ax.plot(live_model[:, 0], live_model[:, 1], color='grey', label='low latency')
ax.plot(stat[sort_idx], far[sort_idx], color='C1', label='relbin search')
ax.set(xlabel='ranking statistic', ylabel='false alarm rate (yr$^{-1}$)',
       xlim=(8., 10.), ylim=(1e-3, 100.),
       yscale='log')
ax.grid()
ax.legend()
plt.show()
#plt.savefig('/home/daniel.finstad/secure_html/relative_binning/full_pipeline/offline_search/old_pipeline_HL_background_phasetd_newsnr.png',
#            dpi=300, bbox_inches='tight')
