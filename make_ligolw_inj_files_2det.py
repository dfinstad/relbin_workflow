#!/usr/bin/env python

import os, sys
import glob
import h5py
import logging
import numpy as np
import pycbc
from pycbc.conversions import mchirp_from_mass1_mass2, eta_from_mass1_mass2
from glue.ligolw import lsctables, ligolw, utils, ilwd
from process_tables import params_table, proc_table as proc_table_data

def _insp_empty_row(obj):
    """Create an empty sim_inspiral or sngl_inspiral row where the columns have
    default values of 0.0 for a float, 0 for an int, '' for a string. The ilwd
    columns have a default where the index is 0.
    """

    # check if sim_inspiral or sngl_inspiral
    if obj == lsctables.SimInspiral:
        row = lsctables.SimInspiral()
        cols = lsctables.SimInspiralTable.validcolumns
    else:
        row = lsctables.SnglInspiral()
        cols = lsctables.SnglInspiralTable.validcolumns

    # populate columns with default values
    for entry in cols.keys():
        if cols[entry] in ['real_4','real_8']:
            if obj == lsctables.SnglInspiral:
                setattr(row,entry,None)
            else:
                setattr(row,entry,0.0)
            #pass
        elif cols[entry] == 'int_4s':
            if obj == lsctables.SnglInspiral:
                setattr(row,entry,None)
            else:
                setattr(row,entry,0)
            #pass
        elif cols[entry] == 'lstring':
            if obj == lsctables.SnglInspiral:
                setattr(row,entry,None)
            else:
                setattr(row,entry,'')
        elif entry == 'process_id':
            if obj == lsctables.SnglInspiral:
                row.process_id = ilwd.ilwdchar("process:process_id:1")
            else:
                row.process_id = ilwd.ilwdchar("sim_inspiral:process_id:0")
        elif entry == 'simulation_id':
            row.simulation_id = ilwd.ilwdchar("sim_inspiral:simulation_id:0")
        elif entry == 'event_id':
            row.event_id = ilwd.ilwdchar("sngl_inspiral:event_id:0")
        else:
            raise ValueError("Column %s not recognized." %(entry) )

    return row

def _coinc_def_rows():
    row1 = lsctables.CoincDef()
    row2 = lsctables.CoincDef()
    cols = lsctables.CoincDefTable.validcolumns
    for entry in cols.keys():
        if 'coinc_def_id' in entry:
            setattr(row1, entry, "coinc_definer:coinc_def_id:0")
            setattr(row2, entry, "coinc_definer:coinc_def_id:1")
        elif 'description' in entry:
            setattr(row1, entry, "sngl_inspiral&lt;--&gt;sngl_inspiral coincidences")
            setattr(row2, entry, "sim_inspiral&lt;--&gt;coinc_event coincidences (exact)")
        elif 'search_coinc_type' in entry:
            setattr(row1, entry, 0)
            setattr(row2, entry, 3)
        elif 'search' in entry:
            setattr(row1, entry, "inspiral")
            setattr(row2, entry, "inspiral")
    return row1, row2

def _coinc_event_map_rows(coinc_ifos):
    #row1 = lsctables.CoincMap()
    #row2 = lsctables.CoincMap()
    nrows = len(coinc_ifos)
    id_map = {'H1': 1, 'L1': 2, 'V1': 3}
    event_ids = [id_map[ifo] for ifo in coinc_ifos]
    rows = []
    for i in range(nrows):
        rows.append(lsctables.CoincMap())
    cols = lsctables.CoincMapTable.validcolumns
    for row, event_id in zip(rows, event_ids):
        for entry in cols.keys():
            if 'coinc_event_id' in entry:
                setattr(row, entry, "coinc_event:coinc_event_id:0")
                #setattr(row2, entry, "coinc_event:coinc_event_id:0")
            elif 'event_id' in entry:
                setattr(row, entry, "sngl_inspiral:event_id:{}".format(event_id))
                #setattr(row2, entry, "sngl_inspiral:event_id:2")
            elif 'table_name' in entry:
                setattr(row, entry, "sngl_inspiral")
                #setattr(row2, entry, "sngl_inspiral")
    return rows

def _coinc_event_row(coinc_ifos):
    row = lsctables.Coinc()
    #cols = ['coinc_def_id', 'coinc_event_id', 'instruments', 'likelihood',
    #        'nevents', 'process_id', 'time_slide_id']
    #entries = ['coinc_definer:coinc_def_id:0', 'coinc_event:coinc_event_id:0',
    #           ifos_str, None, 2, 'process:process_id:1', 'time_slide:time_slide_id:0']
    cols = lsctables.CoincTable.validcolumns
    for entry in cols.keys():
        if 'coinc_def_id' in entry:
            setattr(row, entry, 'coinc_definer:coinc_def_id:0')
        elif 'coinc_event_id' in entry:
            setattr(row, entry, 'coinc_event:coinc_event_id:0')
        elif 'instruments' in entry:
            setattr(row, entry, ",".join(coinc_ifos))
        elif 'likelihood' in entry:
            setattr(row, entry, None)
        elif 'nevents' in entry:
            setattr(row, entry, len(coinc_ifos))
        elif 'process_id' in entry:
            setattr(row, entry, 'process:process_id:1')
        elif 'time_slide_id' in entry:
            setattr(row, entry, 'time_slide:time_slide_id:0')
    return row

def _proc_params_rows():
    rows = []
    cols = ["program", "process_id", "param", "type", "value"]
    for line in params_table:
        row = lsctables.ProcessParams()
        if len(line) < len(cols):
            padlen = len(cols) - len(line)
            padded_line = list(line) + [None] * padlen
        else:
            padded_line = line
        for entry, value in zip(cols, padded_line):
            setattr(row, entry, value)
        rows.append(row)
    return rows

def _proc_rows():
    rows = [lsctables.Process(), lsctables.Process()]
    for k, v in proc_table_data.items():
        setattr(rows[0], k, v[0])
        setattr(rows[1], k, v[1])
    return rows

def _add_snr_series(xmldoc, snr_series, start_time, delta_t,
                     event_id):
    logging.info("Making SNR timeseries entry for event_id {}".format(event_id))
    ts = ligolw.LIGO_LW({'Name': "COMPLEX8TimeSeries"})
    xmldoc.childNodes[0].appendChild(ts)

    time_tag = ligolw.Time({'Name': 'epoch', 'Type': 'GPS'})
    param1_tag = ligolw.Param({'Name': "f0:param", 'Type': "real_8", 'Unit': "s^-1"})
    param1_tag.appendData(str(0))
    param2_tag = ligolw.Param({'Name': "event_id:param", 'Type': "ilwd:char"})
    param2_tag.appendData("sngl_inspiral:event_id:{}".format(event_id))
    array_tag = ligolw.Array({'Name': "snr:array", 'Type': "real_8", 'Unit':""})
    for child in [time_tag, param1_tag, array_tag, param2_tag]:
        ts.appendChild(child)

    time_tag.appendData(str(start_time))
    stream = ligolw.Stream({'Delimiter':" ", 'Type': "Local"})
    dim1 = ligolw.Dim({'Name': "Time", 'Scale': delta_t, 'Start': "0", 'Unit': "s"})
    dim1.appendData(str(len(snr_series)))
    dim2 = ligolw.Dim({'Name': "Time,Real,Imaginary"})
    dim2.appendData(str(3))
    for child in [dim1, dim2, stream]:
        array_tag.appendChild(child)

    for i, s in enumerate(snr_series):
        data_buffer = " " * 8 * 4 + "{} {} {}".format(i*delta_t, s.real, s.imag)
        if i < len(snr_series - 1):
            data_buffer += "\n"
        stream.appendData(data_buffer)
    return

pycbc.init_logging(verbose=True)

# gather necessary files
analysis_dir = sys.argv[1]
output_root = "{}/sky_localization".format(analysis_dir)
output_dir = "{}/ligolw_files".format(output_root)
if os.path.exists(output_root):
    raise OSError("Sky localization directory already exists")
analysis_subdir = os.listdir(analysis_dir)[0]
scratch_dir = "{}/{}/output/local-site-scratch/work/{}-main_ID0000001".format(
    analysis_dir, analysis_subdir, analysis_subdir.replace('.', '_'))
foundinj_dir = glob.glob("{}/*FOUNDINJ_MINIFOLLOWUP*/".format(scratch_dir))[0]
injfind_file = glob.glob("{}/*-HDFINJFIND_BNS*.hdf".format(scratch_dir))[0]
bank_file = glob.glob("{}/*-BANK2HDF-*.hdf".format(scratch_dir))[0]
h1_trig_merge_file = glob.glob("{}/H1-HDF_TRIGGER_MERGE_BNSSTT2_INJ*.hdf".format(scratch_dir))[0]
l1_trig_merge_file = glob.glob("{}/L1-HDF_TRIGGER_MERGE_BNSSTT2_INJ*.hdf".format(scratch_dir))[0]
h1_snr_files = sorted(glob.glob("{}/H1-SINGLE_TEMPLATE_P1_SNR_SERIES_H1_*.hdf".format(foundinj_dir)))
l1_snr_files = sorted(glob.glob("{}/L1-SINGLE_TEMPLATE_P1_SNR_SERIES_L1_*.hdf".format(foundinj_dir)))

# setup output directory
os.mkdir(output_root)
os.mkdir(output_dir)

# read found inj data
with h5py.File(injfind_file, "r") as fp:
    temp_ids = fp['found_after_vetoes/template_id'][:]
    inj_ids = fp['found_after_vetoes/injection_index'][:]
    l1_trig_ids = fp['found_after_vetoes/L1/trigger_id'][:]
    h1_trig_ids = fp['found_after_vetoes/H1/trigger_id'][:]
    l1_times = fp['found_after_vetoes/L1/time'][:]
    h1_times = fp['found_after_vetoes/H1/time'][:]

nfound = len(temp_ids)
logging.info("Analysis has {} found injections".format(nfound))
for i in range(nfound):
        temp_id = temp_ids[i]
        inj_id = inj_ids[i]
        h1_trig_id = h1_trig_ids[i]
        l1_trig_id = l1_trig_ids[i]
        h1_time = h1_times[i]
        l1_time = l1_times[i]

        logging.info("Creating XML document for injection index {}".format(inj_id))
        outdoc = ligolw.Document()
        outdoc.appendChild(ligolw.LIGO_LW())

        logging.info("Adding boilerplate process tables")
        # process params table
        proc_params_table = lsctables.New(lsctables.ProcessParamsTable,
                                          columns=lsctables.ProcessParamsTable.validcolumns)
        params_rows = _proc_params_rows()
        for r in params_rows:
            proc_params_table.append(r)
        outdoc.childNodes[0].appendChild(proc_params_table)
        # process table
        proc_table = lsctables.New(lsctables.ProcessTable,
                                   columns=lsctables.ProcessTable.validcolumns)
        proc_rows = _proc_rows()
        for r in proc_rows:
           proc_table.append(r)
        outdoc.childNodes[0].appendChild(proc_table)

        logging.info("Adding coinc tables")
        coinc_ifos = [ifo.upper() for ifo in ['h1', 'l1'] if
                      eval('{}_time'.format(ifo)) != -1.]
        logging.info("Coinc IFOs are {}".format(coinc_ifos))
        # coinc def
        cd_table = lsctables.New(lsctables.CoincDefTable,
                                 columns=lsctables.CoincDefTable.validcolumns)
        cd1, cd2 = _coinc_def_rows()
        cd_table.append(cd1)
        cd_table.append(cd2)
        outdoc.childNodes[0].appendChild(cd_table)
        # coinc map
        cm_table = lsctables.New(lsctables.CoincMapTable,
                                 columns=lsctables.CoincMapTable.validcolumns)
        cm_rows = _coinc_event_map_rows(coinc_ifos)
        for row in cm_rows:
            cm_table.append(row)
        outdoc.childNodes[0].appendChild(cm_table)
        # coinc event
        ce_table = lsctables.New(lsctables.CoincTable,
                                 columns=lsctables.CoincTable.validcolumns)
        ce1 = _coinc_event_row(coinc_ifos)
        ce_table.append(ce1)
        outdoc.childNodes[0].appendChild(ce_table)

        logging.info("Adding inspiral tables")
        # read data from search pipeline output
        with h5py.File(bank_file, "r") as fp:
            bank_stats = fp.attrs['parameters']
            hl_template_stats = {k: v[temp_id] for k, v in fp.items()}
        bank_stats = list(bank_stats) + ['mchirp', 'eta', 'mtotal']
        hl_template_stats['mchirp'] = mchirp_from_mass1_mass2(hl_template_stats['mass1'],
                                                              hl_template_stats['mass2'])
        hl_template_stats['eta'] = eta_from_mass1_mass2(hl_template_stats['mass1'],
                                                         hl_template_stats['mass2'])
        hl_template_stats['mtotal'] = hl_template_stats['mass1'] + hl_template_stats['mass2']
        trig_stats = ['bank_chisq', 'bank_chisq_dof', 'chisq', 'chisq_dof',
                      'cont_chisq', 'cont_chisq_dof', 'coa_phase', 'template_duration',
                      'sigmasq', 'snr']
        with h5py.File(h1_trig_merge_file, "r") as fp:
            h1_tm = {s: fp['H1/{}'.format(s)][h1_trig_id] for s in trig_stats}
        with h5py.File(l1_trig_merge_file, "r") as fp:
            l1_tm = {s: fp['L1/{}'.format(s)][l1_trig_id] for s in trig_stats}

        # sim inspiral
        sim_table = lsctables.New(lsctables.SimInspiralTable,
                                  columns=lsctables.SimInspiralTable.validcolumns)
        outdoc.childNodes[0].appendChild(sim_table)
        sim = _insp_empty_row(lsctables.SimInspiral)
        for ifo in [ci.lower() for ci in coinc_ifos]:
            exec('sim.{}_end_time = int({}_time)'.format(ifo[0], ifo))
            exec('sim.{}_end_time_ns = int({}_time % 1 * 1e9)'.format(ifo[0], ifo))
        for s in bank_stats:
            exec("sim.{0} = hl_template_stats['{0}']".format(s))
        sim_table.append(sim)

        # sngl inspiral
        sngl_table = lsctables.New(lsctables.SnglInspiralTable,
                                   columns=lsctables.SnglInspiralTable.validcolumns)
        outdoc.childNodes[0].appendChild(sngl_table)
        for i, ifo in enumerate([ci.lower() for ci in coinc_ifos]):
            exec('{}_row = _insp_empty_row(lsctables.SnglInspiral)'.format(ifo))
            exec('{}_row.ifo = "{}"'.format(ifo, ifo.upper()))
            exec('{}_row.event_id = "sngl_inspiral:event_id:{}"'.format(ifo, i+1))
            exec('{0}_row.end_time = int({0}_time)'.format(ifo))
            exec('{0}_row.end_time_ns = int({0}_time % 1 * 1e9)'.format(ifo))
            for s in trig_stats:
                exec("{0}_row.{1} = {0}_tm['{1}']".format(ifo, s))
            for s in bank_stats:
                exec("{0}_row.{1} = hl_template_stats['{1}']".format(ifo, s))
            eval('sngl_table.append({}_row)'.format(ifo))
            # snr timeseries
            snr_file = glob.glob('{0}/{1}-SINGLE_TEMPLATE_P1_SNR_SERIES_{1}_{2}-*.hdf'.format(foundinj_dir, ifo.upper(), inj_id))[0]
            with h5py.File(snr_file, 'r') as fp:
                epoch = fp['snr'].attrs['start_time']
                delta_t = fp['snr'].attrs['delta_t']
                snr_series = fp['snr'][:]
            _add_snr_series(outdoc, snr_series, epoch, delta_t, i+1)

        logging.info("Writing file")
        outfile = "{}/ligolw_injection_{}.xml".format(output_dir, inj_id)
        utils.write_filename(outdoc, outfile, gz=False)

logging.info("Done")

