#!/bin/bash
rm summary.out

for f in CEA-curie_cut CTC-SP2 SDSC-BLUE SDSC-SP2 ;
do
  cd $f
  make simu_metrics
  cd ..
  cat $f/sim_analysis/metrics >> summary.out
done
