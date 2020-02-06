#!/bin/bash

for job in `condor_q -wide | grep "2DET" | awk '{print $1}'`; do
    condor_qedit $job RequestMemory=10000
done
