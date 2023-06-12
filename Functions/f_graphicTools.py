#region Importation of modules
import os
if os.path.basename(os.getcwd())=="BasicFunctionalities":
    os.chdir('..') ## to work at project root  like in any IDE
import sys
if sys.platform != 'win32':
    myhost = os.uname()[1]
else : myhost = ""
if (myhost=="jupyter-sop"):
    ## for https://jupyter-sop.mines-paristech.fr/ users, you need to
    #  (1) run the following in a terminal
    if (os.system("/opt/mosek/9.2/tools/platform/linux64x86/bin/lmgrd -c /opt/mosek/9.2/tools/platform/linux64x86/bin/mosek.lic -l lmgrd.log")==0):
        os.system("/opt/mosek/9.2/tools/platform/linux64x86/bin/lmutil lmstat -c 27007@127.0.0.1 -a")
    #  (2) definition of license
    os.environ["MOSEKLM_LICENSE_FILE"] = '@jupyter-sop'

import numpy as np
import pandas as pd
import csv
import datetime
import copy
import plotly
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from sklearn import linear_model
import sys
import time
import datetime
import seaborn as sb


from Functions.f_optimization import *

def plot_capacity(scenario,outputFolder='output/'):
    v_list = ['capacity_Pvar','energy_Pvar', 'power_Dvar']
    Variables = {v: pd.read_csv(outputFolder + '/' + v + '.csv').drop(columns='Unnamed: 0').set_index('AREA').loc['Marseille'] for v in v_list}

    YEAR=Variables['power_Dvar'].set_index('YEAR_op').index.unique().values
    TECHNO = Variables['power_Dvar'].set_index('TECHNOLOGIES').index.unique().values
    TIMESTAMP=Variables['power_Dvar'].set_index('TIMESTAMP').index.unique().values
    YEAR.sort()
    timestep=round(8760/len(TIMESTAMP))
    

    #region Tracé mix prod H2 et EnR
    df=Variables['capacity_Pvar']
    df=df.pivot(columns='TECHNOLOGIES',values='capacity_Pvar', index=['YEAR_op']).rename(columns={
        "electrolysis_AEL": "Alkaline electrolysis",
        "electrolysis_PEMEL": "PEM electrolysis",
        'SMR': "SMR w/o CCUS",
        'SMR + CCS1':  'SMR + CCUS 50%',
        'SMR + CCS2':  'SMR + CCUS 90%',
    }).fillna(0)

    df['SMR w/o CCUS']+=df['Existing SMR']


    capa=Variables['capacity_Pvar'].set_index(['YEAR_op','TECHNOLOGIES'])

    #LoadFactors
    EnR_loadFactor={y : (Variables['power_Dvar'].groupby(['YEAR_op','TECHNOLOGIES']).sum().drop(columns='TIMESTAMP')['power_Dvar']/(Variables['capacity_Pvar'].set_index(['YEAR_op','TECHNOLOGIES'])['capacity_Pvar']*8760)).reset_index().pivot(index='YEAR_op',columns='TECHNOLOGIES',values=0).loc[y,['Onshore wind','Ground PV','Offshore wind - floating']].fillna(0)  for y in YEAR}
    H2_loadFactor={y : (Variables['power_Dvar'].groupby(['YEAR_op','TECHNOLOGIES']).sum().drop(columns='TIMESTAMP')['power_Dvar']/(Variables['capacity_Pvar'].set_index(['YEAR_op','TECHNOLOGIES'])['capacity_Pvar']*8760)).reset_index().pivot(index='YEAR_op',columns='TECHNOLOGIES',values=0).loc[y,['ElectrolysisM','Existing SMR','SMR','SMR + CCS1','SMR + CCS2']].fillna(0) for y in YEAR}
    for y in YEAR : H2_loadFactor[y].loc[H2_loadFactor[y]<-0.0001]=0
    for y in YEAR : H2_loadFactor[y].loc[H2_loadFactor[y]>1.0001]=0
    for y in YEAR : EnR_loadFactor[y].loc[EnR_loadFactor[y]<-0.0001]=0
    for y in YEAR : EnR_loadFactor[y].loc[EnR_loadFactor[y]>1.0001]=0

    fig, ax = plt.subplots(2,1,sharex=True,figsize=(6.2,4))
    width= 0.40
    labels=list(df.index)
    x = np.arange(len(labels))
    col = plt.cm.tab20c

    # Create dark grey Bar
    l1=list(df['SMR w/o CCUS'])
    ax[0].bar(x - width/2, l1,width, color=col(17), label="SMR w/o CCUS",zorder=2)
    # Create dark bleu Bar
    l2=list(df['SMR + CCUS 50%'])
    ax[0].bar(x - width/2,l2,width, bottom=l1,color=col(0), label="SMR + CCUS 50%",zorder=2)
    #Create turquoise bleu Bar
    l3=list(df['SMR + CCUS 90%'])
    ax[0].bar(x - width/2,l3,width, bottom=[i+j for i,j in zip(l1,l2)], color=col(1) ,label="SMR + CCUS 90%",zorder=2)
    #Create orange Bar
    # l4=list(df['eSMR w/o CCUS'])
    # ax[0].bar(x - width/2,l4,width, bottom=[i+j+k for i,j,k in zip(l1,l2,l3)], color=col[1],label="eSMR w/o CCUS")
    # # Create yellow Bars
    # l5=list(df['eSMR + CCUS 50%'])
    # ax[0].bar(x - width/2,l5,width, bottom=[i+j+k+l for i,j,k,l in zip(l1,l2,l3,l4)], color='#F8B740',label="eSMR + CCUS 50%")
    # Create pink bar
    #l6=list(df['Methane cracking'])
    #ax[0].bar(x - width/2,l6,width, bottom=[i+j+k+l+m for i,j,k,l,m in zip(l1,l2,l3,l4,l5)], color=col[6],label="Methane cracking")
    # Create green Bars
    l7=list(df['ElectrolysisM'])#+df['PEM electrolysis'])
    ax[0].bar(x + width/2,l7,width, color=col(9),label="Water electrolysis",zorder=2)

    # Create red bar
    l8=list(df['Ground PV'])
    ax[1].bar(x ,l8,width, color=col(5),label="Solar",zorder=2)
    # Create violet bar
    l9=list(df['Onshore wind'])
    ax[1].bar(x,l9,width,  bottom=l8,color=col(13),label="Onshore wind",zorder=2)
    # Create pink bar
    l10=list(df['Offshore wind - floating'])
    ax[1].bar(x,l10,width,  bottom=[i+j for i,j in zip(l8,l9)],color=col(14),label="Offshore wind",zorder=2)
    #
    # # Create grey line
    # ax[2].plot(x,list((round(H2_loadFactor[y]['SMR']*100)for y in YEAR)),color=col(17),label='SMR w/o CCUS',zorder=2)
    # # Create dark blue line
    # ax[2].plot(x, list((round(H2_loadFactor[y]['SMR + CCS1'] * 100) for y in YEAR)), color=col(0), label='SMR + CCUS 50%',zorder=2)
    # # Create light blue line
    # ax[2].plot(x, list((round(H2_loadFactor[y]['electrolysis_AEL'] * 100)) for y in YEAR), color=col(9), label='Water electrolysis',zorder=2)
    # Create green line
    # ax[2].plot(x, list((round(H2_loadFactor[y]['SMR + CCS2'] * 100)) for y in YEAR), color=col(1), label='SMR + CCUS 90%',zorder=2)
    # Create WindOnshore line
    # ax[2].plot(x, list((round(EnR_loadFactor[y]['WindOnShore'] * 100)) for y in YEAR),linestyle='--' ,color=col(13), label='Wind Onshore',zorder=2)
    # # Create Solar line
    # ax[2].plot(x, list((round(EnR_loadFactor[y]['Solar'] * 100) for y in YEAR)),linestyle='--',color=col(5), label='Solar',zorder=2)

    #add Load factors
    # for i,y in enumerate(YEAR):
    #     if capa.loc[(y,'electrolysis_AEL'),'capacity_Pvar'] > 100:
    #         ax[0].text((x + width/2)[i], l7[i]/2, str(round(H2_loadFactor[y]['electrolysis_AEL']*100)) +'%',ha='center')
    #     if capa.loc[(y,'SMR'),'capacity_Pvar'] > 100:
    #         ax[0].text((x - width / 2)[i], l1[i] / 2, str(round(H2_loadFactor[y]['SMR'] * 100)) + '%',ha='center',color='white')
    #     if capa.loc[(y,'SMR + CCS1'),'capacity_Pvar'] > 100:
    #         ax[0].text((x - width / 2)[i], l1[i]+l2[i] / 2, str(round(H2_loadFactor[y]['SMR + CCS1'] * 100)) + '%',ha='center',color='white')
    #     if capa.loc[(y, 'Solar'), 'capacity_Pvar'] > 10:
    #         ax[1].text((x)[i], l8[i] / 2, str(round(EnR_loadFactor[y]['Solar'] * 100)) + '%', ha='center')
    #     if capa.loc[(y,'Solar'),'capacity_Pvar'] > 100:
    #         ax[1].text((x)[i], l8[i]/2, str(round(EnR_loadFactor[y]['Solar'] * 100)) + '%', ha='center',color='white')
    #     if capa.loc[(y,'WindOnShore'),'capacity_Pvar'] > 100:
    #         ax[1].text((x)[i], l8[i]+l9[i]/2, str(round(EnR_loadFactor[y]['WindOnShore'] * 100)) + '%', ha='center',color='white')
    #     if capa.loc[(y,'WindOffShore_flot'),'capacity_Pvar'] > 100:
    #         ax[1].text((x)[i], l8[i]+l9[i]+l10[i]/2, str(round(EnR_loadFactor[y]['WindOffShore_flot'] * 100)) + '%', ha='center',color='white')

    ax[0].set_ylim([0,max(max([(n1,n2) for n1,n2 in zip([i+j+k for i,j,k in zip(l2,l2,l3)],l7)]))+100])
    ax[0].grid(axis='y',alpha=0.5,zorder=1)
    ax[1].set_ylim([0,max([i+j+k for i,j,k in zip(l8,l9,l10)])+100])
    ax[1].grid(axis='y',alpha=0.5,zorder=1)
    # ax[2].grid(axis='y', alpha=0.5,zorder=1)
    ax[0].set_ylabel('Installed capacity (MW)')
    ax[1].set_ylabel('Installed capacity (MW)')
    # ax[2].set_ylabel('Load factors (%)')
    ax[0].set_title("Evolution of H2 production assets")
    ax[1].set_title("Evolution of local RE assets")
    # ax[2].set_title("Evolution of load factors")
    plt.xticks(x, ['2010-2020','2020-2030','2030-2040', '2040-2050'])#['2010-2020','2020-2030','2030-2040', '2040-2050']'2050-2060'])
    # Shrink current axis by 20%
    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0, box.width * 0.73, box.height*0.95])
    # Put a legend to the right of the current axis
    ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # Shrink current axis by 20%
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0, box.width * 0.73, box.height*0.95])
    # Put a legend to the right of the current axis
    ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # Shrink current axis by 20%
    # box = ax[2].get_position()
    # ax[2].set_position([box.x0, box.y0, box.width * 0.73, box.height*0.95])
    # Put a legend to the right of the current axis
    # ax[2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(outputFolder+'/Evolution mix prod.png')
    plt.show()

    
    def monthly_average(df):
        df['month'] = df.index // 730 + 1
        # df.iloc[8760,'month']=12
        return df.groupby('month').mean()


    loadFactors_df=Variables['power_Dvar'].copy().pivot(index=['YEAR_op','TIMESTAMP'],columns='TECHNOLOGIES',values='power_Dvar')
    for y in YEAR :
        for tech in TECHNO:
            loadFactors_df.loc[y,slice(None)][tech]=(Variables['power_Dvar'].set_index(['YEAR_op','TIMESTAMP','TECHNOLOGIES']).loc[(y,slice(None),tech),'power_Dvar']/(Variables['capacity_Pvar'].set_index(['YEAR_op','TECHNOLOGIES']).loc[(y,tech),'capacity_Pvar'])).reset_index().drop(columns=['TECHNOLOGIES','YEAR_op']).set_index('TIMESTAMP')['power_Dvar']

    print(Variables['power_Dvar'].set_index(['YEAR_op','TIMESTAMP','TECHNOLOGIES']).loc[(y,slice(None),tech),'power_Dvar'])

    month=np.unique(TIMESTAMP//730+1)


    fig, ax = plt.subplots()

    for k,y in enumerate(YEAR):
        #Create electrolysis graph
        l1=list(monthly_average(loadFactors_df.loc[(y,slice(None))])['ElectrolysisM']*100)
        plt.plot(month,l1,color=col(8+k),label=y,zorder=2)

    plt.grid(axis='y',alpha=0.5,zorder=1)
    plt.ylabel('Load factor (%)')
    plt.xlabel('Months')
    plt.xticks(month,['January','February','March','April','May','June','July','August','September','October','November','December'],rotation=45)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0+0.1, box.width * 0.90, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(outputFolder+'/elec_LoadFactor.png')
    plt.show()

    return df

def plot_energy(outputFolder='Data/output/'):
    v_list = ['capacityInvest_Dvar', 'transInvest_Dvar', 'capacity_Pvar', 'capacityDel_Pvar', 'capacityDem_Dvar',
              'energy_Pvar', 'power_Dvar', 'storageConsumption_Pvar', 'storageIn_Pvar', 'storageOut_Pvar',
              'stockLevel_Pvar', 'importation_Dvar', 'Cmax_Pvar', 'carbon_Pvar', 'powerCosts_Pvar', 'capacityCosts_Pvar',
              'importCosts_Pvar', 'storageCosts_Pvar', 'turpeCosts_Pvar', 'Pmax_Pvar', 'max_PS_Dvar', 'carbonCosts_Pvar','exportation_Dvar']
    Variables = {v: pd.read_csv(outputFolder + '/' + v + '.csv').drop(columns='Unnamed: 0') for v in v_list}

    YEAR=Variables['power_Dvar'].set_index('YEAR_op').index.unique().values
    YEAR.sort()

    df = Variables['power_Dvar'].groupby(['YEAR_op', 'TECHNOLOGIES']).sum().drop(columns='TIMESTAMP').reset_index()
    df = df.pivot(columns='TECHNOLOGIES', values='power_Dvar', index='YEAR_op').rename(columns={
        "electrolysis_AEL": "Alkaline electrolysis",
        "electrolysis_PEMEL": "PEM electrolysis",
        'SMR': "SMR w/o CCUS",
        'SMR + CCS1': 'SMR + CCUS 50%',
        'SMR + CCS2': 'SMR + CCUS 90%',
        'SMR_elec': 'eSMR w/o CCUS',
        'SMR_elecCCS1': 'eSMR + CCUS 50%',
        'cracking': 'Methane cracking'
    }).fillna(0)

    df = df / 1000000

    df_renewables=Variables['power_Dvar'].pivot(index=['YEAR_op','TIMESTAMP'],columns='TECHNOLOGIES',values='power_Dvar')[['WindOnShore','WindOffShore_flot','Solar']].reset_index().groupby('YEAR_op').sum().drop(columns='TIMESTAMP').sum(axis=1)
    df_export=Variables['exportation_Dvar'].groupby(['YEAR_op','RESOURCES']).sum().loc[(slice(None),'electricity'),'exportation_Dvar'].reset_index().drop(columns='RESOURCES').set_index('YEAR_op')
    df_feedRE=(df_renewables-df_export['exportation_Dvar'])/1.54/1000000#

    df_biogas=Variables['importation_Dvar'].groupby(['YEAR_op','RESOURCES']).sum().loc[(slice(None),'gazBio'),'importation_Dvar'].reset_index().set_index('YEAR_op').drop(columns='RESOURCES')
    for y in YEAR:
        fugitives = 0.03 * (1 - (y - YEAR[0]) / (2050 - YEAR[0]))*df_biogas.loc[y]['importation_Dvar']
        temp=df_biogas.loc[y]['importation_Dvar']-fugitives
        if temp/1.28/1000000<df.loc[y]['SMR w/o CCUS']:
            df_biogas.loc[y]['importation_Dvar']=temp/1.28/1000000
        else:
            temp2=temp-df.loc[y]['SMR w/o CCUS']*1.28*1000000
            if temp2/1.32/1000000<df.loc[y]['SMR + CCUS 50%']:
                df_biogas.loc[y]['importation_Dvar']=df.loc[y]['SMR w/o CCUS']+temp2/1.32/1000000
            else:
                temp3=temp-df.loc[y]['SMR w/o CCUS']*1.28*1000000-df.loc[y]['SMR + CCUS 50%']*1.32*1000000
                if temp3/1.45/1000000<df.loc[y]['SMR + CCUS 90%']:
                    df_biogas.loc[y]['importation_Dvar']=df.loc[y]['SMR w/o CCUS']+df.loc[y]['SMR + CCUS 50%']+temp3/1.45/1000000
                else :
                    df_biogas.loc[y]['importation_Dvar'] = df.loc[y]['SMR w/o CCUS']+df.loc[y]['SMR + CCUS 50%']+df.loc[y]['SMR + CCUS 90%']

    fig, ax = plt.subplots(figsize=(6,4))
    width = 0.35
    col=plt.cm.tab20c
    labels = list(df.index)
    x = np.arange(len(labels))

    # Create dark grey Bar
    l1 = list(df['SMR w/o CCUS'])
    ax.bar(x - width / 2, l1, width, color=col(17), label="SMR w/o CCUS",zorder=2)
    # Create dark bleu Bar
    l2 = list(df['SMR + CCUS 50%'])
    ax.bar(x - width / 2, l2, width, bottom=l1, color=col(0), label="SMR + CCUS 50%",zorder=2)
    # Create turquoise bleu Bar
    l3 = list(df['SMR + CCUS 90%'])
    ax.bar(x - width / 2, l3, width, bottom=[i + j for i, j in zip(l1, l2)], color=col(1), label="SMR + CCUS 90%",zorder=2)
    # Create biogas Bars
    l8=list(df_biogas['importation_Dvar'])
    plt.rcParams['hatch.linewidth']=8
    plt.rcParams['hatch.color'] = col(3)
    ax.bar(x - width / 2,l8,width,color='none',hatch='/',edgecolor=col(3),linewidth=0.5,label="Biomethane feed",alpha=0.8,zorder=3)
    # # Create orange Bar
    # l4 = list(df['eSMR w/o CCUS'])
    # ax.bar(x - width / 2, l4, width, bottom=[i + j + k for i, j, k in zip(l1, l2, l3)], color=col[1],
    #        label="eSMR w/o CCUS")
    # # Create yellow Bars
    # l5 = list(df['eSMR + CCUS 50%'])
    # ax.bar(x - width / 2, l5, width, bottom=[i + j + k + l for i, j, k, l in zip(l1, l2, l3, l4)], color=col[8],
    #        label="eSMR + CCUS 50%")
    # Create pink bar
    # l6 = list(df['Methane cracking'])
    # ax.bar(x - width / 2, l6, width, bottom=[i + j + k + l + m for i, j, k, l, m in zip(l1, l2, l3, l4, l5)],
    #        color=col[6], label="Methane cracking")
    # Create light green Bars
    l7 = list(df['Alkaline electrolysis']+ df['PEM electrolysis'])
    ax.bar(x + width / 2, l7, width, color=col(8), label="AEL grid feed",zorder=2)
    # Create dark green bar
    l9=list(df_feedRE)
    ax.bar(x + width / 2,l9,width,color=col(9),label="AEL local feed",zorder=3)

    plt.grid(axis='y',alpha=0.5,zorder=1)
    ax.set_ylabel('H2 production (TWh/yr)')
    # ax.set_title("Use of assets")
    plt.xticks(x,['2020','2030']) #['2020-2030', '2030-2040', '2040-2050', '2050-2060'])#,'2060'])
    m=max(max(l7),max([l1[i]+l2[i]+l3[i] for i in np.arange(len(l1))]))
    ax.set_ylim([0,int(m)+0.5])
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.72, box.height])
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(outputFolder+'/H2 production.png')
    plt.show()

    return df
