#!/bin/bash
paste <(awk '{print $1,$2,$3,$4,$5,$6,$7,$8}' curie_cut.swf) <(cat prediction_sgd) <(awk '{print $10,$11,$12,$13,$14,$15,$16,$17,$18}' curie_cut.swf)
