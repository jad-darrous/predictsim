#!/bin/bash

for f in CEA-curie_cut CTC-SP2 KTH-SP2 SDSC-BLUE SDSC-SP2 ;
do
  cd $f
  make simulate
done
