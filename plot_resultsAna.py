import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


from scenarios_ref_PACA import *
from Functions.f_graphicTools import *

ouputPath = 'Data/output/'

outputFolder = ouputPath+'test_10_1zone_LP'

capa=plot_capacity(scenarioPACA,outputFolder)
