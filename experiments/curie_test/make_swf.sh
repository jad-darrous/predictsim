#!/bin/bash
awk '{print $1,$2,$3,$4,$5,$6,$7,$8}' curie_cut.swf > /tmp/swftmp1
awk '{print $10,$11,$12,$13,$14,$15,$16,$17,$18}' curie_cut.swf > /tmp/swftmp1b
paste /tmp/swftmp1 prediction_sgd /tmp/swftmp1b
rm /tmp/swftmp1 /tmp/swftmp1b
