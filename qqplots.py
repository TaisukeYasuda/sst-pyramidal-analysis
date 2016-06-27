
#########################################################################
# Statistics on simulated distribution using qq plots
# 06/26/2016
# Taisuke Yasuda
#########################################################################

import cell_statistics as cs
import numpy as np
import math
import matplotlib.pyplot as plt
import os
import pandas as pd

############ data to use ############

model_names = ['pq','xq','px','xx','ptq','qtp']
cell_data = cs.cell_data()
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

for model in models:
    params = pd.read_excel('../params/'+model+'.xlsx')
    for cell in cells:
        sheet_name = cell+'_1trials'
