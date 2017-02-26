
#########################################################################
# CDF analysis of constant model.
# Taisuke Yasuda
#########################################################################

import numpy as np
from scipy import stats
import math
import random
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os
import sys
import pandas as pd
import qqplotlib as qq

############ data to use ############

def get_cell_data():
    return pd.read_excel('./data.xlsx',sheetname=None)

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
path = './results/constant/feb-26-2017'

#### response amplitudes over trial, over repetition ####

for cell in cells:
    print(cell)
    data = cell_data[cell]

    for i in range(1,num_trials+1):
        print('\t'+str(i))
        sheet = data[i].tolist()
        plot_count = 0

        # ks statistics
        k = []
        #### plot simulations ####
        for N in range(N_min,N_max+1):
            print('\t\t'+str(N))
            plot_count += 1
            subplot = '33'+str(plot_count)
            ax = fig.add_subplot(subplot)
            ax.cla()
            ax.set_title('QQ Plot Assuming '+str(N)+' Contacts')
            result = params(sheet,N)
            qqplot = qq.qqplot(result)

            quantiles = qqplot['quantiles']

            # set aside one for legend
            sim_data_handle = ax.scatter(quantiles,qqplot['samples'][0],marker='.',color='lightblue')
            for sample in qqplot['samples'][1:]:
                ax.scatter(quantiles,sample,marker='.',color='lightblue')
            curve1 = [x[0] for x in qqplot['intervals']]
            curve2 = [x[1] for x in qqplot['intervals']]
            ax.plot(quantiles,curve1,color='blue')
            ax.plot(quantiles,curve2,color='blue')
            obs_data_handle = ax.scatter(quantiles,qqplot['obs_nonzero'],linewidths=2,color='red')
            ax.plot(quantiles,qqplot['obs_nonzero'],linewidth=2,color='red')

            maximum = qqplot['maximum']
            ax.plot([0,maximum],[0,maximum],color='black')
            ax.set_xlim([0,max(quantiles)+0.1])
            ax.set_ylim([0,maximum])

            ax.set_xlabel('simulated data quantiles (mV)')
            ax.set_ylabel('observed data quantiles (mV)')

            # ks computation
            obs = qqplot['obs_nonzero']
            sim = qqplot['samples']
            sim = reduce((lambda x, y: x + y), sim)
            k.append(stats.ks_2samp(obs,sim)[1])

        legend = fig.legend((sim_data_handle, obs_data_handle),
            ('simulated data', 'observed data'),
            loc = 'lower center',
            bbox_to_anchor = (0,-0.05,1,1),
            bbox_transform = plt.gcf().transFigure)
        plt.tight_layout()
        plt.savefig(path+'/qq/'+cell+'-'+str(i)+'-qq.png', bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.clf()

        # ks plot
        ind = np.arange(N_max-N_min+1)  # the x locations for the groups
        width = 0.35                    # the width of the bars

        ax = fig.add_subplot('111')
        rects1 = ax.bar(ind, k, width, color='r')

        # add some text for labels, title and axes ticks
        ax.set_ylabel('KS p value')
        ax.set_xlabel('N')
        ax.set_xticks(ind + (width/2))
        ax.set_xticklabels(('3', '4', '5', '6', '7', '8', '9', '10', '11'))
        plt.savefig(path+'/ks/'+cell+'-'+str(i)+'-ks.png')
        plt.clf()
