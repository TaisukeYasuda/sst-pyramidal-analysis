
#########################################################################
# Statistics on simulated distribution using qq plots
# 06/26/2016
# Taisuke Yasuda
#########################################################################

import numpy as np
import math
import random
import matplotlib.pyplot as plt
import os
import pandas as pd

############ data to use ############

def get_cell_data():
    return pd.read_excel('./cleaned_amplitude_data.xlsx',sheetname=None)

models = ['pq','xq','px','xx','ptq','qtp']
cell_data = get_cell_data()
cells = cell_data.keys()

def cell_response(p,q,n):
    '''simulate a single cell response'''
    assert(len(p) == n and len(q) == n)

    response = 0
    for i in range(n):
        p[i] = min(max(p[i],0),1)
        q[i] = max(q[i],0)
        if (np.random.binomial(1,p[i])):
            response += q[i]
    return response

def simulate(p,q,n):
    '''simulate data'''
    #### preconditions ####
    assert(type(n) == int)

    #### if p or q is fixed, then just repeat it n times ####
    if (type(p) == int or type(p) == float or type(p) == np.float64):
        p = [p]*n
    if (type(p) == int or type(q) == float or type(q) == np.float64):
        q = [q]*n

    num_simulate = 10000
    num_zeros = 0
    nonzero = list()
    for i in xrange(num_simulate):
        x = cell_response(p,q,n)
        if (x == 0):
            num_zeros += 1
        else:
            nonzero.append(x)
    return num_zeros, nonzero

#### script for qq plot statistical analysis ####

for model in models:
    params = pd.read_excel('../params/'+model+'.xlsx',sheetname=None)
    for cell in cells:
        plt.cla()
        #### read data ####
        param = params[cell+'_1trials']
        data = cell_data[cell][1].tolist()
        #### extract data ####
        p, q = param['p'], param['q']
        n = 10
        sim_num_zeros, sim_nonzero = simulate(p,q,n)
        sim_nonzero = pd.Series(sim_nonzero)
        obs_num_zeros = data.count(0)
        obs_nonzero = sorted([x for x in data if x != 0])

        num_quantiles = len(obs_nonzero)
        quantile = 1.0 / num_quantiles
        quantiles = [quantile * i for i in range(1,num_quantiles+1)]
        values = sorted([sim_nonzero.quantile(q) for q in quantiles])

        #### qq plot ####
        plt.xlabel('Quantiles of Simulated Distribution')
        plt.ylabel('Quantiles of Observed Distribution')
        plt.title('QQ Plot for '+cell+' with model '+model)

        #### compute confidence intervals ####
        samples = list()
        sim_nonzero = sim_nonzero.tolist()
        for i in xrange(1000):
            sample = list()
            for j in xrange(num_quantiles):
                sample.append(np.random.choice(sim_nonzero))
            sample = sorted(sample)
            plt.scatter(values,sample,color='blue')
            samples.append(sample)
        # samples = np.array(samples).transpose()

        plt.scatter(values,obs_nonzero,color='red')
        plt.savefig('./qqplots/'+model+'/'+cell+'.png')

print('done!')
