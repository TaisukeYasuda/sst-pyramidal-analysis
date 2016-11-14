
#########################################################################
# QQ plot analysis of distribution guessing constant values.
# 08/04/2016
# Update variance s: better estimate from data.
# 08/12/2016
# Set lower y_lim and fix limits for qq plots
# 10/01/2016
# Update variance s: fix bug
# 11/01/2016
# Make look better
# 11/03/2016
# Taisuke Yasuda
#########################################################################

import numpy as np
import math
import random
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd
import qqplotlib as qq

############ data to use ############

def get_cell_data():
    return pd.read_excel('./cleaned_amplitude_data.xlsx',sheetname=None)

def prob(p_f,N):
    return 1 - p_f**(1.0/N)

def resp(A,p,N):
    return A*1.0/(N*p)

def fail(sheet):
    return sheet.count(0.0)*1.0/len(sheet)

def avg(sheet):
    return np.mean(np.array(sheet))

def var(sheet):
    return np.var(np.array(sheet))

def params(sheet,N):
    num = len(sheet)
    p_f = fail(sheet)
    A = avg(sheet)
    p = prob(p_f,N)
    q = resp(A,p,N)
    v = var(sheet)
    s = (v*1.0 / (N*p) - q**2 + q**2*p)**0.5

    result = dict()
    result['p'] = p
    result['q'] = q
    result['n'] = N
    result['s'] = s
    result['num_sim'] = 10000
    result['num_sample'] = 1000
    result['data'] = sheet
    return result

cell_data = get_cell_data()
cells = cell_data.keys()
num_trials = 10

fig = plt.figure(figsize=(15,12))
plt.axis('off')

N_min, N_max = 3,11
path = './try-all-constant/qq-plots/nov-03-2016/'

#### response amplitudes over trial, over repetition ####
for cell in cells:
    print(cell)
    data = cell_data[cell]
    for i in range(1,num_trials+1):
        print('\t'+str(i))
        sheet = data[i].tolist()
        plot_count = 0
        #### plot original ####
        # plot_count += 1
        # subplot = '33'+str(plot_count)
        # ax = fig.add_subplot(subplot)
        # ax.cla()
        # ax.set_title('Original Data')
        # binwidth = 0.01
        # bins=np.arange(min(sheet)-binwidth, max(sheet) + 2*binwidth, binwidth)
        # ax.hist(sheet,bins,color='blue')
        # ax.set_ylim([0,20])

        #### plot simulations ####
        for N in range(N_min,N_max+1):
            plot_count += 1
            subplot = '33'+str(plot_count)
            ax = fig.add_subplot(subplot)
            ax.cla()
            ax.set_title('N = '+str(N))
            result = params(sheet,N)
            qqplot = qq.qqplot(result)

            quantiles = qqplot['quantiles']
            # for sample in qqplot['samples']:
            #     ax.scatter(quantiles,sample,marker='.',color='blue')
            # for j in range(len(quantiles)):
            #     ax.plot([quantiles[j],quantiles[j]],qqplot['intervals'][j],
            #         marker='_',color='yellow')
            # ax.scatter(quantiles,qqplot['obs_nonzero'],color='red')

            # nov 03 2016 ver
            for sample in qqplot['samples']:
                ax.scatter(quantiles,sample,marker='.',color='lightblue')
            curve1 = [x[0] for x in qqplot['intervals']]
            curve2 = [x[1] for x in qqplot['intervals']]
            ax.plot(quantiles,curve1,color='blue')
            ax.plot(quantiles,curve2,color='blue')
            ax.plot(quantiles,qqplot['obs_nonzero'],linewidth=2,color='red')
            #

            maximum = qqplot['maximum']
            ax.plot([0,maximum],[0,maximum],color='black')
            ax.set_xlim([0,max(quantiles)+0.1])
            ax.set_ylim([0,maximum])

        plt.savefig(path+cell+'-'+str(i)+'-qq.png')
