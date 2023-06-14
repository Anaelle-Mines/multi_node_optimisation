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
# solver= 'mosek'

solver= 'appsi_highs'
solverpath_folder='C:\\Users\\anaelle.jodry\\Documents\\highs.mswin64.20230531'
sys.path.append(solverpath_folder)

print('Building model...')
model = systemModel(scenarioPACA,isAbstract=False)
# model.write("test_model.mps", io_options = {"symbolic_solver_labels":True})
start_clock = time.time()
print('Calculating...')
# h = highspy.Highs()
# filename = 'test_model.mps'
# h.readModel(filename)
# h.run()
# print('Model ', filename, ' has status ', h.getModelStatus())
# solution = h.getSolution()
# info = h.getInfo()
# basis = h.getBasis()
opt = SolverFactory(solver)
results = opt.solve(model)
end_clock = time.time()
print('Computational time: {:.0f} s'.format(end_clock - start_clock)) 

# print('Optimal objective = ', info.objective_function_value)
# # num_var = h.getNumCol()
# # for icol in range(num_var):
# #     print(icol, solution.col_value[icol], h.basisStatusToString(basis.col_status[icol]))

# h.writeSolution(solution,'test')

res = {
    'variables': getVariables_panda(model), 
}

print(res)
# try: 
#     res['constraints'] = getConstraintsDual_panda(model)
# except KeyError: # This exception will be raised for a MILP case
#     pass 

outputFolder = 'out_test_highs'

try: 
    os.mkdir(outputFolder)
except: 
    pass

for v in res['variables'].keys():
    print(v)

for k, v in res['variables'].items():
    print ('Writing ' + k + '...') 
    v.to_csv(outputFolder + '/' + k + '.csv',index=True)

# print(res['variables']['capacity_Pvar'])