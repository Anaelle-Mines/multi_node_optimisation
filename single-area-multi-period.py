import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import time 
import os 
# import highspy

from Functions.f_multiResourceModelsAna import systemModel,loadScenario
from Functions.f_optimization import getVariables_panda, getConstraintsDual_panda

from scenarios_ref_PACA import scenarioPACA
# from scenarios import scenario

outputPath='Data/output/'
outputFolder = outputPath+'test_100_1zone_LP'

# solver= 'mosek'
solver= 'appsi_highs'

if solver=='appsi_highs' :
    solverpath_folder='C:\\Users\\anaelle.jodry\\Documents\\highs.mswin64.20230531'
    sys.path.append(solverpath_folder)

print('Building model...')
model = systemModel(scenarioPACA,isAbstract=False)
start_clock = time.time()
print('Calculating...')
opt = SolverFactory(solver)
results = opt.solve(model)
end_clock = time.time()
print('Computational time: {:.0f} s'.format(end_clock - start_clock)) 


res = {
    'variables': getVariables_panda(model), 
}

clock=pd.DataFrame(['time',end_clock - start_clock])

res['variables'].update({'Computational time (s)':clock})

try: 
    res['constraints'] = getConstraintsDual_panda(model)
except KeyError: # This exception will be raised for a MILP case
    pass 


try: 
    os.mkdir(outputFolder)
except: 
    pass

for v in res['variables'].keys():
    print(v)

for k, v in res['variables'].items():
    print ('Writing ' + k + '...') 
    v.to_csv(outputFolder + '/' + k + '.csv',index=True)
