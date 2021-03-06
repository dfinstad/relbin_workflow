#!/usr/bin/env python

params_table = [("inspinj","process:process_id:0","--output","string","inj.xml"),
                ("inspinj","process:process_id:0","--m-distr","string","fixMasses"),
                ("inspinj","process:process_id:0","--fixed-mass1","float","1.400000"),
                ("inspinj","process:process_id:0","--fixed-mass2","float","1.400000"),
                ("inspinj","process:process_id:0","--time-step","float","3.600000e+03"),
                ("inspinj","process:process_id:0","--gps-start-time","int","1000000000"),
                ("inspinj","process:process_id:0","--gps-end-time","int","1000086400"),
                ("inspinj","process:process_id:0","--d-distr","string","volume"),
                ("inspinj","process:process_id:0","--min-distance","float","2.000000e+05"),
                ("inspinj","process:process_id:0","--max-distance","float","6.000000e+05"),
                ("inspinj","process:process_id:0","--l-distr","string","random"),
                ("inspinj","process:process_id:0","--i-distr","string","uniform"),
                ("inspinj","process:process_id:0","--f-lower","float","30.000000"),
                ("inspinj","process:process_id:0","--disable-spin","string",""),
                ("inspinj","process:process_id:0","--waveform","string","TaylorF2threePointFivePN"),
                ("bayestar-realize-coincs","process:process_id:1","--loglevel","lstring","INFO"),
                ("bayestar-realize-coincs","process:process_id:1","--input","lstring","inj.xml"),
                ("bayestar-realize-coincs","process:process_id:1","--output","lstring","coinc_conda.xml"),
                ("bayestar-realize-coincs","process:process_id:1","--jobs","int_8s","1"),
                ("bayestar-realize-coincs","process:process_id:1","--detector","lstring","H1"),
                ("bayestar-realize-coincs","process:process_id:1","--detector","lstring","L1"),
                ("bayestar-realize-coincs","process:process_id:1","--detector","lstring","V1"),
                ("bayestar-realize-coincs","process:process_id:1","--snr-threshold","real_8","4.0"),
                ("bayestar-realize-coincs","process:process_id:1","--net-snr-threshold","real_8","8.0"),
                ("bayestar-realize-coincs","process:process_id:1","--keep-subthreshold"),
                ("bayestar-realize-coincs","process:process_id:1","--min-triggers","int_8s","2"),
                ("bayestar-realize-coincs","process:process_id:1","--min-distance","real_8","0.0"),
                ("bayestar-realize-coincs","process:process_id:1","--max-distance","real_8","inf"),
                ("bayestar-realize-coincs","process:process_id:1","--measurement-error","lstring","gaussian-noise"),
                ("bayestar-realize-coincs","process:process_id:1","--enable-snr-series"),
                ("bayestar-realize-coincs","process:process_id:1","--reference-psd","lstring","psd.xml"),
                ("bayestar-realize-coincs","process:process_id:1","--duty-cycle","real_8","1.0"),
                ("bayestar-realize-coincs","process:process_id:1","--preserve-ids")]

proc_table = {
    "program": ("inspinj", "bayestar-realize-coincs"),
    "version": ("ba160287551f30ebb687ad38cebd5b50b05ec3cc", "ligo.skymap 0.1.14"),
    "cvs_repository": ("CLEAN: All modifications committed", None),
    "cvs_entry_time": (1170440256, None),
    "comment": (" ", "Simulated coincidences"),
    "is_online": (0, 0),
    "node": ("sugwg-condor.phy.syr.edu", "sugwg-condor.phy.syr.edu"),
    "username": ("50001", "daniel.finstad"),
    "unix_procid": (570989, 571175),
    "start_time": (1259476506, 1259476589),
    "end_time": (1259476506, 1259476606),
    "jobid": (0, 0),
    "domain": ("lalapps", None),
    "ifos": ("", "H1,L1,V1"),
    "process_id": ("process:process_id:0", "process:process_id:1")
}
