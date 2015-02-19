rightside=['abs','square','exp']
leftside=['abs','square','exp']
leftparam=['0.0001','0,001','0.01','0.1','1','10','100','1000']
rightparam=['0.0001','0,001','0.01','0.1','1','10','100','1000']
threshold=['-6400','-600','-60','-10','0','10','60','600','6400']
weight=["1+10*log(r/m)","1+10*log(m/r)","1+10*log(1/(r*m))","1+10*log(m*r)"]
scheduler = [{
	#"name":'easy_prediction_backfill_scheduler',
	#The predictor (if needed) to use.
	#To list them: for s in predictors/predictor_*.py ; do basename -s .py $s; done
	'predictor': {"name":"predictor_sgdlinear", "max_cores":"auto","eta":5000, "loss":"composite","rightside":rs,"rightparam":rp,"leftside":ls,"leftparam":lp,"threshold":tr, "weight":"1", "quadratic":False,"cubic": False,"gd": "NAG","regularization":"l2","lambda":4000000000},

	#The corrector (if needed) to use.
	#Choose between: "+str(schedulers.common_correctors.correctors_list())
        'corrector': {"name":"recursive_doubling"},
	}
        for rs in rightside
        for rp in rightparam
        for ls in leftside
        for lp in leftside
        for tr in threshold
        if (not rs=="exp" and rp>0.01)
        if (not ls=="exp" and lp>0.01)
        ]
