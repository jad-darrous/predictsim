#!/usr/bin/python
# encoding: utf-8
import numpy as np

def run_data(filename,alg,replay=False,period1=100,period2=1000):
    data1_dtype=np.dtype([('y',np.float32),
        ('x1',np.float32),
        ('x2',np.float32)])
    with open (filename, "r") as f:
        data=np.loadtxt(f, dtype=data1_dtype,comments=";")
    #print data['y']
    X=np.vstack((data['x1'],data['x2'])).T
    Y=data['y']
    replay1=True
    replay2=True
    i=1
    j=1
    while i < len(X):
        if replay:
            if i % period1 ==0:
                #print("period1 %s " %i)
                if replay1:
                    i=i-period1+1
                replay1=not replay1
            if i % period2 ==0:
                #print("period2 %s " %i)
                if replay2:
                    i=i-period2+1
                replay2=not replay2
        p=alg.predict(X[i])
        alg.fit(X[i],Y[i])
        i+=1
        j+=1
    print j

def run_ssgd(dataset,loss,model="linear",alpha=1,regularizer=None,verbose=False,scaler="scale_mean0",replay=False,period1=1,period2=1):
    #regularized sgd
    from algos.ssgd import SSGD
    print("dataset %s using model %s, %s-regularized sgd squared loss and scaling %s. eta=0.01 and replay=%s"%(dataset,model,regularizer,scaler,replay))

    if model=="linear":
        from models.linear_model import LinearModel
        m=LinearModel(2)
    elif model=="affine":
        from models.affine_model import AffineModel
        m=AffineModel(2)
    else:
        raise ValueError("no valid model specified")

    if loss=="squared_loss":
        from losses.squared_loss import SquaredLoss
        ls=SquaredLoss(m)
    elif loss=="abs_loss":
        from losses.abs_loss import AbsLoss
        ls=AbsLoss(m)
    else:
        raise ValueError("no valid loss specified")

    if regularizer=="l2":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l2 import L2
        l=RegularizedLoss(m,ls,L2(),alpha)
    elif regularizer=="l1":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l1 import L1
        l=RegularizedLoss(m,ls,L1(),alpha)
    elif regularizer==None:
        l=ls
    else:
        raise ValueError("invalid regularization specified")

    alg=SSGD(m,l,1,verbose=verbose,scaler=scaler)

    run_data("datasets/%s"%dataset,alg,replay=replay)
    print("The parameter vector after training is")
    print(m.get_param_vector())
    del m, ls, l, alg

def run_sgd(dataset,loss,model="linear",alpha=1,regularizer=None,verbose=False):
    #regularized sgd
    from algos.sgd import SGD
    print("dataset %s using model %s, %s-regularized sgd squared loss. eta=0.01"%(dataset,model,regularizer))

    if model=="linear":
        from models.linear_model import LinearModel
        m=LinearModel(2)
    elif model=="affine":
        from models.affine_model import AffineModel
        m=AffineModel(2)
    else:
        raise ValueError("no valid model specified")

    if loss=="squared_loss":
        from losses.squared_loss import SquaredLoss
        ls=SquaredLoss(m)
    elif loss=="abs_loss":
        from losses.abs_loss import AbsLoss
        ls=AbsLoss(m)
    else:
        raise ValueError("no valid loss specified")

    if regularizer=="l2":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l2 import L2
        l=RegularizedLoss(m,ls,L2(),alpha)
    elif regularizer=="l1":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l1 import L1
        l=RegularizedLoss(m,ls,L1(),alpha)
    elif regularizer==None:
        l=ls
    else:
        raise ValueError("invalid regularization specified")

    alg=SGD(m,l,1,verbose=verbose)

    run_data("datasets/%s"%dataset,alg)
    print("The parameter vector after training is")
    print(m.get_param_vector())
    del m, ls, l, alg


def run_ng(dataset,loss,alpha=1,regularizer=None,verbose=False,eta=0.01):
    #normalized gradient from langford paper of     print("dataset %s using model lineara,  normalized gradient algorithm with %s-regularized %s loss."%(dataset,regularizer,loss))

    from models.linear_model import LinearModel
    m=LinearModel(2)

    if loss=="squared_loss":
        from losses.squared_loss import SquaredLoss
        ls=SquaredLoss(m)
    elif loss=="abs_loss":
        from losses.abs_loss import AbsLoss
        ls=AbsLoss(m)
    else:
        raise ValueError("no valid loss specified")

    if regularizer=="l2":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l2 import L2
        l=RegularizedLoss(m,ls,L2(),alpha)
    elif regularizer=="l1":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l1 import L1
        l=RegularizedLoss(m,ls,L1(),alpha)
    elif regularizer==None:
        l=ls
    else:
        raise ValueError("invalid regularization specified")

    from algos.ng import NG
    alg=NG(m,l,eta,verbose=verbose)

    run_data("datasets/%s"%dataset,alg)
    print("The parameter vector after training is")
    print(m.get_param_vector())
    del m, ls, l, alg


def run_nag(dataset,loss,alpha=1,regularizer=None,verbose=False,eta=0.01):
    #normalized gradient from langford paper of     print("dataset %s using model lineara,  normalized gradient algorithm with %s-regularized %s loss."%(dataset,regularizer,loss))

    from models.linear_model import LinearModel
    m=LinearModel(2)

    if loss=="squared_loss":
        from losses.squared_loss import SquaredLoss
        ls=SquaredLoss(m)
    elif loss=="abs_loss":
        from losses.abs_loss import AbsLoss
        ls=AbsLoss(m)
    else:
        raise ValueError("no valid loss specified")

    if regularizer=="l2":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l2 import L2
        l=RegularizedLoss(m,ls,L2(),alpha)
    elif regularizer=="l1":
        from losses.regularized_loss import RegularizedLoss
        from losses.regularizations.l1 import L1
        l=RegularizedLoss(m,ls,L1(),alpha)
    elif regularizer==None:
        l=ls
    else:
        raise ValueError("invalid regularization specified")

    from algos.nag import NAG
    alg=NAG(m,l,eta,verbose=verbose)

    run_data("datasets/%s"%dataset,alg)
    print("The parameter vector after training is")
    print(m.get_param_vector())
    del m, ls, l, alg




def test_all():
    #run_sgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False)
    #run_sgd("data1-linear","squared_loss",model="affine",regularizer=None,verbose=False)
    #run_sgd("data2-affine","squared_loss",model="affine",regularizer=None,verbose=False)
    #run_sgd("data2-affine","squared_loss",model="linear",regularizer=None,verbose=False)
    #run_sgd("data2-affine","squared_loss",model="linear",regularizer="l2",verbose=False)
    #run_sgd("data2-affine","squared_loss",model="linear",regularizer="l1",verbose=False)
    #run_sgd("data3-linear-perturbed","squared_loss",model="linear",regularizer=None,verbose=False)
    #run_sgd("data3-linear-perturbed","squared_loss",model="linear",regularizer="l2",verbose=False)
    #run_sgd("data3-linear-perturbed","squared_loss",model="linear",regularizer="l2",verbose=False)
    #run_sgd("data4-affine-powerlaw","squared_loss",model="affine",regularizer=None,verbose=False)
    #run_sgd("data4-affine-powerlaw","squared_loss",model="affine",alpha=20,regularizer="l1",verbose=False)
    #run_sgd("data4-affine-powerlaw","squared_loss",model="affine",alpha=20,regularizer="l2",verbose=False)
    #run_sgd("data5-linear-powerlaw","squared_loss",model="linear",alpha=30,regularizer="l2",verbose=False)
    #run_ng("data5-linear-powerlaw","squared_loss",verbose=False,eta=0.06)
    #run_nag("data5-linear-powerlaw","squared_loss",verbose=False,eta=100000)


#SSGD
#Without replay
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_mean0")
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_mean0")
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_rescale01")
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_rescale01")
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_unitlength")
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_unitlength")
#With replay
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_mean0",replay=True)
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_mean0",replay=True)
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_rescale01",replay=True)
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_rescale01",replay=True)
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_unitlength",replay=True)
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_unitlength",replay=True)
    #run_ssgd("data1-linear","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_standardize11",replay=True,period1=888,period2=1200)
    #run_ssgd("data5-linear-powerlaw","squared_loss",model="linear",regularizer=None,verbose=False,scaler="scale_standardize11",replay=True,period1=888,period2=1200)

    #run_nag("data5-linear-powerlaw","squared_loss",verbose=False,alpha=1,regularizer=None,eta=0.01)
    run_nag("data5-linear-powerlaw","squared_loss",verbose=False,eta=100000)

if __name__=="__main__":
    test_all()
