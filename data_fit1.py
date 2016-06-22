
#########################################################################
# Fitting the cell distributions to examine p and q values, given the
# number of contacts n, improved fit pq
# 06/07/2016
# Taisuke Yasuda
#########################################################################

import cell_statistics as cs
import scipy.optimize as opt
import numpy as np
import math
import matplotlib.pyplot as plt
from numpy.random import normal, binomial
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

############ data to use ############

model_names = ['pq','xq','px','xx']
colors = {'pq':'green','px':'blue','xq':'yellow','xx':'red'}
extract_pool = {
    'pq':'fit.p = p_opt[0:Cell.N];fit.q = p_opt[Cell.N:2*Cell.N]',
    'px':'fit.p = p_opt[0:Cell.N];fit.q = p_opt[Cell.N]',
    'xq':'fit.p = p_opt[0];fit.q = p_opt[1:Cell.N+1]',
    'xx':'fit.p = fit.avg_p;fit.q = fit.avg_q'
}
init_pool = {
    'pq':'result = p+q',
    'px':'result = p+[self.avg_q]',
    'xq':'result = q',
    'xx':None
}
obj_func_pool = {
    'pq':'''def obj_func(x,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,
        q0,q1,q2,q3,q4,q5,q6,q7,q8,q9):
        fit.p = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9]
        fit.q = [q0,q1,q2,q3,q4,q5,q6,q7,q8,q9]
        result = fit.simulate()
        return eval_hist(result,x)''',
    'px':'''def obj_func(x,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,q):
        fit.p = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9]
        fit.q = q
        result = fit.simulate()
        return eval_hist(result,x)''',
    'xq':'''def obj_func(x,q0,q1,q2,q3,q4,q5,q6,q7,q8,q9):
        fit.p = fit.avg_p
        fit.q = [q0,q1,q2,q3,q4,q5,q6,q7,q8,q9]
        result = fit.simulate()
        return eval_hist(result,x)''',
    'xx':None
}
bounds_pool = {
    'pq':'''lo_bound = [0]*(2*Cell.N);up_bound = [1]*(Cell.N) + [np.inf]*(Cell.N)''',
    'px':'''lo_bound = [0]*(Cell.N + 1);up_bound = [1]*(Cell.N) + [np.inf]''',
    'xq':'''lo_bound = [0]*(Cell.N);up_bound = [np.inf]*(Cell.N)''',
    'xx':None
}

############## helper functions ################

def eval_hist(hist,xdata):
    '''return array of images of values under histogram function'''
    result = list()
    xdata = xdata[0:len(xdata)-1]
    for x in xdata:
        if (x < FitDist.LO or x > FitDist.HI):
            result.append(0)
        else:
            index = int(math.floor(x/FitDist.STEP))
            result.append(hist[index])
    return result

def trim_hist_index(hist):
    '''trim off blank parts of the histogram'''
    num_bins = len(hist)
    for i in range(num_bins):
        if (np.array_equal(hist[i:],[0]*(num_bins - i))):
          return i

################### classes to organize data ###################

class FitModel:
    ''' class for organizing models for fitting distribution '''

    def __init__(self,name,color,obj_func,init,extract,bounds):
        self.name = name
        self.color = color
        #### strings of code that vary for each model ####
        self.obj_func = obj_func
        self.init = init
        self.extract = extract
        self.bounds = bounds

class Cell:
    ''' class for organizing cell data'''
    #### number of synaptic contacts ####
    N = 10

    def __init__(self,name,data):
        self.name = name
        #### data is the response amplitudes data ####
        self.data = data
        #### bound is the x axis cutoff to make the histogram look nice ####
        self.bound = math.ceil(max(cs.flatten(data)))

    def hist(self,bins):
        '''return a histogram of the cells'''
        data = cs.flatten(self.data)
        return np.histogram(data,bins)[0]

class FitDist:
    '''class for organizing fitting distributions'''
    #### standard deviation of initial distribution of p and q ####
    STDVAR_P = 0.01
    STDVAR_Q = 0.3
    #### standard deviation of cell response ####
    STDVAR_C = 0.05
    #### histogram bins ####
    LO,HI,STEP = 0,8,0.1
    BINS = np.arange(LO,HI,STEP)
    #### path for figures and data ####
    HIST = './histograms'
    XLSX = './params'
    #### matplotlib figure for saving histograms ####
    fig = plt.figure()
    ax = fig.add_subplot(111)

    def __init__(self,cell,model,trials):
        self.cell = cell
        self.model = model
        self.trials = trials

        #### select only specified trials ####
        trials = list(range(1,self.trials+1))
        self.cell_select = cell.data[trials]
        self.num_responses = len(cs.flatten(self.cell_select))

        self.rep = 1

        #### uninitialized ####
        self.avg_p = None
        self.avg_q = None
        self.init_vec = None
        self.p = None
        self.q = None
        self.hist = None
        self.responses = None

        #### compute values ####
        self.comp_avg()
        return

    def comp_avg(self):
        '''compute the average probability and response of the cell'''
        cell_data = cs.flatten(self.cell_select)
        total = 0
        for response in cell_data:
            if (response != 0):
                total += response
        zero_count = cell_data.count(0)
        nonzero_count = self.num_responses - zero_count
        fail_rate = zero_count*1.0/self.num_responses
        self.avg_p = 1 - fail_rate**(1.0/Cell.N)
        self.avg_q = total*1.0/nonzero_count
        return

    def init_vectors(self):
        '''initialize the parameters vector for fitting'''
        p,q = list(),list()
        for i in range(Cell.N):
            #### initial probabilities are normally distributed ####
            temp = normal(self.avg_p,FitDist.STDVAR_P)
            temp = min(max(temp,0),1)
            p.append(temp)
            #### initial responses are normally distributed ####
            temp = normal(self.avg_q,FitDist.STDVAR_Q)
            temp = max(temp,0)
            q.append(temp)
        #### initialize differently depending on model ####
        exec(self.model.init)
        return result

    def define_obj_func(self):
        '''define the objective function to fit'''
        exec(self.model.obj_func)
        return obj_func

    def define_bounds(self):
        exec(self.model.bounds)
        assert(self.model.name != 'xx')
        return (lo_bound,up_bound)

    def simulate(self):
        '''simulate cell response'''
        #### if a variable is fixed, then just repeat it N times ####
        p, q = self.p, self.q
        if (self.model.name[0] == 'x'):
            p = [self.p]*Cell.N
        if (self.model.name[1] == 'x'):
            q = [self.q]*Cell.N
        #### simulation ####
        hist = None
        responses = list()
        for r in range(self.rep):
            for i in range(self.num_responses):
                response = 0
                for j in range(Cell.N):
                    p[j] = min(max(p[j],0),1)
                    q[j] = max(q[j],0)
                    if (binomial(1,p[j])):
                        response += normal(q[j],FitDist.STDVAR_C)
                responses.append(response)
        self.responses = responses
        result = np.histogram(responses,FitDist.BINS,weights=[1.0/self.rep]*len(responses))[0]
        #### save simulation ####
        self.hist = result
        return result

    def extract_params(self):
        '''extract p and q from the fitted parameters'''
        exec(self.model.extract)

    def save_name(self):
        '''name to be used to save the data'''
        return self.cell.name + '_' + str(self.trials) + 'trials'

    def save_excel(self,excel):
        '''save the parameters to an excel file'''
        params = dict()
        params['p'] = self.p
        params['q'] = self.q
        if (self.model.name == 'xx'):
            params['p'] = [params['p']]
            params['q'] = [params['q']]
        params = pd.DataFrame(params)
        params.to_excel(excel,sheet_name=self.save_name())
        return

    def save_hist(self):
        '''save the simulated histogram image'''
        self.simulate()
        FitDist.ax.set_xlabel('Response Amplitude (mV)')
        FitDist.ax.set_ylabel('Frequency')
        FitDist.ax.set_title(self.cell.name)
        bins = np.arange(0,self.cell.bound,FitDist.STEP)
        FitDist.ax.hist(self.responses,bins,weights=[1.0/self.rep]*len(self.responses),
            facecolor=self.model.color)
        #FitDist.ax.set_xlim((0,self.cell.bound))
        path = os.path.join(FitDist.HIST,self.model.name)
        #### save histogram ####
        FitDist.fig.savefig(os.path.join(path,self.save_name()+'.png'))
        #### save the zoomed histogram ####
        FitDist.ax.set_ylim([0,20])
        FitDist.fig.savefig(os.path.join(path,self.save_name()+'_zoom.png'))
        FitDist.ax.cla()
        return

    def save_original(self):
        '''save the original histogram image'''
        FitDist.ax.set_xlabel('Response Amplitude (mV)')
        FitDist.ax.set_ylabel('Frequency')
        FitDist.ax.set_title(self.cell.name)
        FitDist.ax.hist(cs.flatten(self.cell_select),
            np.arange(0,self.cell.bound,FitDist.STEP),facecolor='black')
        #### save histogram ####
        path = os.path.join(FitDist.HIST,'raw_data/')
        FitDist.fig.savefig(os.path.join(path,self.save_name()+'.png'))
        # save zoom in version
        FitDist.ax.set_ylim([0,20])
        FitDist.fig.savefig(os.path.join(path,self.save_name()+'_zoom.png'))
        FitDist.ax.cla()

    def save_nrmsqe(self,squared_error):
        '''compute and store the normalized root mean squared error'''
        xdata, ydata = FitDist.BINS, self.cell.hist(FitDist.BINS)
        #### trim off region after max response ####
        i = trim_hist_index(ydata)
        xdata, ydata = xdata[:i], ydata[:i]
        #### compute normalized root mean squared error ####
        obs, exp = eval_hist(self.hist,xdata), ydata
        num_bins = len(obs)
        error = 0
        for i in range(num_bins):
            error += (obs[i]-exp[i])**2
        nrmsqe = (error**0.5)/(num_bins*self.num_responses)
        #### store ####
        squared_error[self.model.name][self.cell.name][self.trials] = nrmsqe

################# prepare data #################

data = cs.cell_data()
cell_names = data.keys()
trials = [1,2,4,10]

#### cells ####
cells = list()
for cell_name in cell_names:
    cells.append(Cell(cell_name,data[cell_name]))

#### models ####
models = list()
for model_name in model_names:
    color = colors[model_name]
    obj_func = obj_func_pool[model_name]
    init = init_pool[model_name]
    extract = extract_pool[model_name]
    bounds = bounds_pool[model_name]
    models.append(FitModel(model_name,color,obj_func,init,extract,bounds))

################ fit curve and visualize #################

squared_error = dict()

for model in models:
    #### excel writer for exporting data ####
    XLSX = './params/'
    path = os.path.join(XLSX,model.name+'.xlsx')
    excel = pd.ExcelWriter(path)
    print(model.name)
    for cell in cells:
        print('\t'+cell.name)
        if (model.name not in squared_error):
            squared_error[model.name] = dict()
        squared_error[model.name][cell.name] = dict()

        for num_trials in trials:
            print('\t\t'+str(num_trials))
            fit = FitDist(cell,model,num_trials)
            xdata, ydata = FitDist.BINS, cell.hist(FitDist.BINS)

            #### if not everything is fixed, fit the distribution ####
            p_opt = None
            if (model.name != 'xx'):
                p0 = fit.init_vectors()
                obj_func = fit.define_obj_func()
                bounds = fit.define_bounds()
                p_opt,p_cov = opt.curve_fit(obj_func,xdata,ydata,p0=p0,bounds=bounds)
                if (model.name == 'xq'):
                    p_opt = [fit.avg_p] + p_opt.tolist()

            #### save the parameters ####
            fit.extract_params()
            fit.save_excel(excel)
            #### save the resulting histogram ####
            fit.save_hist()
            #### save the original data histogram ####
            fit.save_original()
            #### compute the normalized root mean squared error ####
            fit.save_nrmsqe(squared_error)

    excel.save()

############### prepare figures ###############

#### prepare pdf file ####
c = canvas.Canvas("research_figures.pdf")
pdf_width,pdf_height = letter

#### prepare five panel figures ####
FIG = './figures/'

title_space = 10
title = 50
height = 300
width = 500
hspace = 50
vspace = 50
h_label = 50
v_label = 50
img_height = 3*vspace + 3*height + title + h_label
img_width = 3*hspace + 2*width + v_label
font = ImageFont.truetype("ubuntu-font-family/Ubuntu-L.ttf",24)
l_font = ImageFont.truetype("ubuntu-font-family/Ubuntu-L.ttf",20)
e_font = ImageFont.truetype("ubuntu-font-family/Ubuntu-L.ttf",20)
black = (0,0,0)

top = title_space+title+height+vspace
bot = title_space+title+height+vspace+height+vspace
left = v_label+hspace
right = v_label+hspace+width+hspace

box = {'pq':(left,top), 'px':(right,top), 'xq':(left,bot), 'xx':(right,bot)}

adjust_pos = 80

top += height
bot += height
left += adjust_pos
right += adjust_pos

nrmsqe = {'pq':(left,top), 'px':(right,top), 'xq':(left,bot), 'xx':(right,bot)}

for num_trial in trials:
    for cell in cells:
        for zoom in [True,False]:
            #### make a new figure ####
            fig = Image.new('RGB',(img_width,img_height),'white')
            draw = ImageDraw.Draw(fig)

            #### add the title ####
            figure_title = 'Cell '+cell.name+' with '+str(num_trial)+' Trials'
            if (zoom):
                figure_title += ', Zoomed In'
            title_align,blah = font.getsize(figure_title)
            draw.text(((img_width - title_align)/2,title_space),figure_title,black,font=font)

            #### add original data histogram ####
            img_path = os.path.join(FitDist.HIST,'raw_data/')
            img_file = cell.name+'_'+str(num_trial)+'trials'
            if (zoom):
                img_file += '_zoom'
            img_path = os.path.join(img_path,img_file+'.png')
            fig.paste(Image.open(img_path).resize((width,height)),((img_width-width)/2,title_space+title))

            #### add labels to figure ####
            row = title_space+vspace+height+vspace+height/2
            col = 10
            draw.text((col,row),'vary p',black,font=l_font)
            row += vspace+height
            draw.text((col,row),'fix p',black,font=l_font)
            row += height/2+vspace
            col += h_label+width/2
            draw.text((col,row),'vary q',black,font=l_font)
            col += hspace+width
            draw.text((col,row),'fix q',black,font=l_font)
            for model in models:
                #### add histogram fitted by model ####
                img_path = os.path.join(FitDist.HIST,model.name)
                img_file = cell.name+'_'+str(num_trial)+'trials'
                if (zoom):
                    img_file += '_zoom'
                img_path = os.path.join(img_path,img_file+'.png')
                fig.paste(Image.open(img_path).resize((width,height)),box[model.name])

                #### add squared error ####
                error = squared_error[model.name][cell.name][num_trial]
                text = 'Normallized RMS Error: ' + str(error)
                draw.text(nrmsqe[model.name],text,black,font=e_font)

            #### save images ####
            fig_file = cell.name+'-'+str(num_trial)
            if (zoom):
                fig_file += '-zoom'
            fig.save(os.path.join(FIG,fig_file+'.png'))

            margin = 10
            #### paste image to pdf ####
            img_ratio = img_height*1.0/img_width
            pdf_img_width = pdf_width - 2*margin
            pdf_img_height = round(img_ratio * pdf_img_width)
            fig = ImageReader(fig)
            c.drawImage(fig,margin,pdf_height-margin-pdf_img_height,width=pdf_img_width,height=pdf_img_height)
            c.showPage()

#### prepare bar graphs ####

fig = plt.figure()
ax = fig.add_subplot(111)
for num_trial in trials:
    ax.set_ylabel('Average Normalized Root Mean Squared Error')
    ax.set_title('Error Across Fit Models, Taking the First '+str(num_trial)+' Trials')
    means = list()
    stds = list()
    for model in models:
        errors = list()
        for cell in cells:
            errors.append(squared_error[model.name][cell.name][num_trial])
        means.append(np.mean(errors))
        stds.append(np.std(errors))
    indices = np.arange(len(models))
    ax.bar(indices,means,color='g',yerr=stds)
    ax.set_xticks(indices+0.5)
    ax.set_xticklabels(('pq','xq','px','xx'))

    #### save images ####
    file_name = 'error_fig-'+str(num_trial)+'_trials.png'
    fig.savefig(file_name)
    ax.cla()

    #### paste image to pdf ####
    plot = Image.open(file_name)
    width,height = plot.size
    plot = ImageReader(plot)

    img_ratio = height*1.0/width
    pdf_img_width = pdf_width-2*margin
    pdf_img_height = round(img_ratio * pdf_img_width)
    c.drawImage(plot,(pdf_width-pdf_img_width)/2,pdf_height-pdf_img_height-margin,width=pdf_img_width,height=pdf_img_height)

    c.showPage()

#### close figures pdf ####
c.save()
