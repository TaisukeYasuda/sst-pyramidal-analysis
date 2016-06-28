
#########################################################################
# Statistics on simulated distribution using qq plots
# 06/26/2016
# Taisuke Yasuda
#########################################################################

import numpy as np
import math
import matplotlib.pyplot as plt
import os
import pandas as pd

############ data to use ############

def get_cell_data():
    return pd.read_excel('./cleaned_amplitude_data.xlsx')

model_names = ['pq','xq','px','xx','ptq','qtp']
cell_data = get_cell_data()
cells = cell_data.keys()

def cell_response(p,q,n):
    '''simulate a single cell response'''
    #### preconditions ####
    assert(type(p) == list or type(p) == np.ndarray)
    assert(type(q) == list or type(q) == np.ndarray)
    assert(len(p) == n && len(q) == n)

    response = 0
    for i in range(n):
        p[i] = min(max(p[i],0),1)
        q[i] = max(q[i],0)
        if (binomial(1,p[i])):
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
            nonzero += x
    return num_zeros, nonzero

#### script for qq plot statistical analysis ####

fig = plt.figure()
ax = fig.add_subplot(111)

for model in models:
    params = pd.read_excel('../params/'+model+'.xlsx')
    for cell in cells:
        ax.cla()
        #### read data ####
        param = params[cell+'_1trials']
        data = cell_data[cell][1].tolist()
        #### extract data ####
        p, q = param['p'], param['q']
        n = 10
        sim_num_zeros, sim_nonzero = simulate(p,q,n)
        sim_nonzero = pd.Series(sim_nonzero)
        obs_num_zeros = data.count(0)
        obs_nonzero = [x for x in data if x != 0]

        num_quantiles = len(obs_nonzero)
        quantile = 1.0 / num_quantiles
        quantiles = [quantile * i for i in range(1,num_quantiles+1)]
        values = [sim_nonzero.quantile(q) for q in quantiles]

        #### plot observed quantiles against simulated quantiles ####
        ax.set_xlabel('Quantiles of Simulated Distribution')
        ax.set_ylabel('Quantiles of Observed Distribution')
        ax.set_title('QQ Plot for ' + cell)
        ax.plot(values,obs_nonzero,color='blue')
