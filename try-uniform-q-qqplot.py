
#########################################################################
# QQ plot and KS analysis of uniform model.
# Taisuke Yasuda
#########################################################################

import numpy as np
from scipy import stats
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

def resp(A,p,N,w):
    q = list()
    mean = A*1.0/(N*p)
    interval = w*1.0/(N-1)
    offset = w*0.5
    for i in range(N):
        q.append(interval*i + mean - offset)
    return q

def fail(sheet):
    return sheet.count(0.0)*1.0/len(sheet)

def avg(sheet):
    return np.mean(np.array(sheet))

def var(sheet):
    return np.var(np.array(sheet))

def params(sheet,N,w):
    num = len(sheet)
    p_f = fail(sheet)
    A = avg(sheet)
    p = prob(p_f,N)
    q = resp(A,p,N,w)
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
path = './results/uniform/nov-14-2016/'

#### response amplitudes over trial, over repetition ####
for cell in cells:
    data = cell_data[cell]
    print(cell)
    for i in range(1,num_trials+1):
        print(str(i))
        sheet = data[i].tolist()
        A = avg(sheet)
        p_f = fail(sheet)

        #### plot simulations ####
        for N in range(N_min,N_max+1):
            print('\t'+str(N))
            plot_count = 0

            p = prob(p_f,N)
            mean = A*1.0/(N*p)
            num_widths = 9
            widths = np.arange(0,2*mean,2*mean*1.0/num_widths).tolist()

            # ks statistics
            k = []
            for w in widths:
                plot_count += 1
                subplot = '33'+str(plot_count)
                ax = fig.add_subplot(subplot)
                ax.cla()
                ax.set_title('N = '+str(N)+', w = '+str(w))
                result = params(sheet,N,w)
                qqplot = qq.qqplot(result)

                quantiles = qqplot['quantiles']

                # nov 03 2016 ver
                for sample in qqplot['samples']:
                    ax.scatter(quantiles,sample,marker='.',color='lightblue')
                curve1 = [x[0] for x in qqplot['intervals']]
                curve2 = [x[1] for x in qqplot['intervals']]
                ax.plot(quantiles,curve1,color='blue')
                ax.plot(quantiles,curve2,color='blue')
                ax.plot(quantiles,qqplot['obs_nonzero'],linewidth=2,color='red')

                maximum = qqplot['maximum']
                ax.plot([0,maximum],[0,maximum],color='black')
                ax.set_xlim([0,max(quantiles)+0.1])
                ax.set_ylim([0,maximum])

                # ks statistics
                quantiles = qqplot['quantiles']
                obs = qqplot['obs_nonzero']
                sim = qqplot['samples']

                sim = reduce((lambda x, y: x + y), sim)
                k.append(stats.ks_2samp(obs,sim)[1])

            fig.suptitle(cell+', Trial '+str(i)+', N = '+str(N))
            plt.savefig(path+'/qq/'+cell+'-'+str(i)+'-'+str(N)+'-qq.png')
            fig.clf()

            ax.plot(widths,k,color='green')
            ax.set_xlabel('distribution width')
            ax.set_ylabel('KS test p value')

            fig.suptitle(cell+', Trial '+str(i)+', N = '+str(N))
            plt.savefig(path+/ks/+cell+'-'+str(i)+'-'+str(N)+'-ks.png')
            fig.clf()
