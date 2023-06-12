import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


from scenarios_ref_PACA import *
from Functions.f_graphicTools import *

ouputPath = 'output/'

outputFolder=ouputPath+'out'

capa=plot_capacity(scenarioPACA,outputFolder)
