rightside=['abs','square','exp']
leftside=['abs','square','exp']
leftparam=[0.0001,0.01,1,100,10000]
rightparam=[0.0001,0.01,1,100,10000]
threshold=[0,60,600]
weight=["5+log(r/m)","5+log(m/r)","11+log(1/(r*m))","1+log(m*r)"]
sgdlinear_configs= [
        {
            "name":"predictor_sgdlinear",
            "max_cores":"auto",
            "eta":5000,
            "loss":"composite",
            "rightside":rs,
            "rightparam":rp,
            "leftside":ls,
            "leftparam":lp,
            "threshold":tr,
            "weight":w,
            "quadratic":True,
            "cubic": False,
            "gd": "NAG",
            "regularization":"l2",
            "lambda":4000000000
            }
        for rs in rightside
        for rp in rightparam
        for ls in leftside
        for lp in leftparam
        for tr in threshold
        for w in weight
        if not( rs=="exp"    and rp>0.01)
        if not( ls=="exp"    and lp>0.01)
        if not( ls=="abs"    and lp<1)
        if not( ls=="square" and lp<1)
        if not( rs=="abs"    and rp<1)
        if not( rs=="square" and rp<1)
        ]

predictors_with_correctors= sgdlinear_configs+[{"name":"predictor_tsafrir"}]
predictors_without_correctors = [{"name":"predictor_clairvoyant"}, {"name":"predictor_reqtime"}, {"name":"predictor_double_reqtime"}]
scheds_without_predictors = ['easy_backfill_scheduler', "easy_sjbf_scheduler"]
scheds_with_predictors = ['easy_plus_plus_scheduler', 'easy_prediction_backfill_scheduler']
correctors = ("reqtime", "tsafrir", "recursive_doubling")

sched_configs=[
	{
			"name":s,
			"predictor":None, #schedulers without prediction
			"corrector":None
	}
	for s in scheds_without_predictors
	]+[{
			"name":s,
			"predictor": p, #schedulers wiht upper-bounding predictions
			"corrector": {'name':"throw_an_error"}
	}
	for p in predictors_without_correctors
	for s in scheds_with_predictors
	]+[{
			"name":s,
			"predictor":p,  #schedulers with non-guarante on predictions
			"corrector": {'name':c}
	}
	for p in predictors_with_correctors
	for s in scheds_with_predictors
	for c in correctors]
