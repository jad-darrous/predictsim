#!/bin/bash
rm summary.out

for f in CEA-curie_sample CEA-curie CEA-curie_cut CTC-SP2 KTH-SP2 SDSC-BLUE SDSC-SP2 ;
do
  cd $f
  make clean
  cd ..
done
