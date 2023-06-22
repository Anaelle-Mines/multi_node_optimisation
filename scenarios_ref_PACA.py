
import numpy as np
import pandas as pd
import tech_eco_data
from scipy.interpolate import interp1d


nHours = 8760

timeStep = 4  # For now only integers work
t = np.arange(1, nHours + 1, timeStep)
nHours = len(t)

yearZero = 2010
yearFinal = 2050
yearStep = 10
# +1 to include the final year
yearList = [yr for yr in range(yearZero, yearFinal+yearStep, yearStep)]
nYears = len(yearList)
areaList = ["Marseille"]


scenarioPACA = {}
scenarioPACA['areaList'] = areaList
scenarioPACA['timeStep'] = timeStep
scenarioPACA['lastTime'] = t[-1]

dist = {"Nice": {"Marseille": 200, "Alpin": 200, "Nice": 0}, "Marseille": {"Nice": 200,
                                                                           "Alpin": 200, "Marseille": 0}, "Alpin": {"Nice": 200, "Marseille": 200, "Alpin": 0}}
scenarioPACA['distances'] = pd.concat(
    (
        pd.DataFrame(data={
            'area1': area1,
            'area2': area2,
            'distances': dist[area1][area2]
        }, index=(area1, area2)
        ) for area1 in areaList
        for area2 in areaList
    )
)
scenarioPACA['distances'] = scenarioPACA['distances'].reset_index().drop_duplicates(
    subset=['area1', 'area2']).set_index(['area1', 'area2']).drop(columns='index')

# donne la liste des couples de noeuds
couples_noeuds = list(scenarioPACA['distances'].index)

yearL=[2020,2030,2040,2050]

hourlyDemand_H2=interp1d(yearL, [360 * (1 + 0.025) ** (k * yearStep) for k in np.arange(len(yearL))], fill_value=(360,755),bounds_error=False)


def demande_h_area(area, year):
    """returns hydrogen yearly demand of an area in MWh"""
    # tab numpy pour broadcast

    if area == "Nice":
        return  np.zeros(nHours)  
    elif area == "Alpin":
        return np.zeros(nHours) 
    else:
        return hourlyDemand_H2(year+yearStep/2) * np.ones(nHours) 


def stockage_h_area(area):
    if area == "Fos":
        return 100000  # unité ?
    else:
        return 0


scenarioPACA['resourceDemand'] = pd.concat(
    (
        pd.DataFrame(data={
            'AREA': area,
            'YEAR': year,
            # We add the TIMESTAMP so that it can be used as an index later.
            'TIMESTAMP': t,
            'electricity': np.zeros(nHours),
            # Hourly constant but increasing demand
            'hydrogen': demande_h_area(area, year),
            'gas': np.zeros(nHours),
        }
        ) for k, year in enumerate(yearList[1:])
        for area in areaList
    )
)


'''
print(scenarioPACA['resourceDemand'])
print(scenarioPACA['resourceDemand'].head())
print(scenarioPACA['resourceDemand'].tail())
'''
scenarioPACA['conversionTechs'] = []


for area in areaList:
    for k, year in enumerate(yearList[:-1]):
        tech = "Offshore wind - floating"
        maxcap = [0,500,500,500]
        if area != "Marseille":
            maxcap = [0,0,0,0]

        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
            tech, hyp='ref', year=year+yearStep/2)
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Electricity production',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': maxcap[k],
                                'EmissionCO2': 0, 'Conversion': {'electricity': 1, 'hydrogen': 0},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 1e3,  # capacité max d'une zone et d'une techno (MW)
                                # puissance fonctionnelle maximale produite par une unité
                                }
                               }
                         )
        )


        tech = "Onshore wind"
        maxcap = [0,100,100,100]
        if area == "Alpin":
            maxcap = [0,0,0,0]
        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
            tech, hyp='ref', year=year+yearStep/2)
        if area == "Nice":
            capex *= 1.5
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Electricity production',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': maxcap[k],
                                'EmissionCO2': 0, 'Conversion': {'electricity': 1, 'hydrogen': 0},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 150
                                },
                               }
                         )
        )

        tech = "Ground PV"
        maxcap = [0,100,100,100]
        if area == "Alpin":
            maxcap = [0,0,0,0]
        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
            tech, hyp='ref', year=year+yearStep/2)
        if area == "Nice":
            capex *= 2
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Electricity production',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': maxcap[k],
                                'EmissionCO2': 0, 'Conversion': {'electricity': 1, 'hydrogen': 0},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 150
                                },
                               }
                         )
        )

        # tech = "ElectrolysisS"
        # capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
        #     tech, hyp='ref', year=year+yearStep/2)
        # scenarioPACA['conversionTechs'].append(
        #     pd.DataFrame(data={tech:
        #                        {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
        #                         'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
        #                         'minCapacity': 0, 'maxCapacity': 500,  # cap à investir
        #                         'EmissionCO2': 0, 'Conversion': {'electricity': -1 / tech_eco_data.conv_el_h, 'hydrogen': 1},
        #                         'EnergyNbhourCap': 0,  # used for hydroelectricity
        #                         'capacityLim': 10e3
        #                         },
        #                        }
        #                  )
        # )

        tech = "ElectrolysisM"
        maxcap = [0,1e4,1e4,1e4]
        if area == "Alpin":
            maxcap = [0,0,0,0]
        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
            tech, hyp='ref', year=year+yearStep/2)
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': maxcap[k],
                                'EmissionCO2': 0, 'Conversion': {'electricity': -1.54, 'hydrogen': 1},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 10e4
                                },
                               }
                         )
        )

        # tech = "ElectrolysisL"
        # capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
        #     tech, hyp='ref', year=year+yearStep/2)
        # scenarioPACA['conversionTechs'].append(
        #     pd.DataFrame(data={tech:
        #                        {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
        #                         'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
        #                         'minCapacity': 0, 'maxCapacity': 500,
        #                         'EmissionCO2': 0, 'Conversion': {'electricity': -1 / tech_eco_data.conv_el_h, 'hydrogen': 1},
        #                         'EnergyNbhourCap': 0,  # used for hydroelectricity
        #                         'capacityLim': 10e3
        #                         },
        #                        }
        #                  )
        # )

        tech = "SMR"
        capex, opex, LifeSpan = 800e3, 40e3, 60
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': 100e3,
                                'EmissionCO2': 0, 'Conversion': {'electricity': 0, 'hydrogen': 1, 'gas': -1.28},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 100e3,'RampConstraintPlus':0.3
                                },
                               }
                         )
        )

        tech = "Existing SMR"
        capex, opex, LifeSpan = 0e3, 40e3, 30
        scenarioPACA['conversionTechs'].append(

            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 410 if (year == yearZero and area == 'Marseille') else 0, 'maxCapacity': 410 if (year == yearZero and area == 'Marseille') else 0,
                                'EmissionCO2': 0, 'Conversion': {'electricity': 0, 'hydrogen': 1, 'gas': -1.28},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 410 if (area == 'Marseille') else 0,'RampConstraintPlus':0.3
                                },
                               }
                         )
        )

        tech = "SMR + CCS1"
        capex, opex, LifeSpan = 900e3, 45e3, 60
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                                'LifeSpan': LifeSpan, 'powerCost': 7.71, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': 100e3,
                                'EmissionCO2': -150, 'Conversion': {'electricity': 0, 'hydrogen': 1, 'gas': -1.32},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 100e3,'RampConstraintPlus':0.3
                                },
                               }
                         )
        )

        tech = "SMR + CCS2"
        capex, opex, LifeSpan = 1000e3, 50e3, 60
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                                'LifeSpan': LifeSpan, 'powerCost': 13.07, 'investCost': capex, 'operationCost': opex,
                                'minCapacity': 0, 'maxCapacity': 100e3,
                                'EmissionCO2': -270, 'Conversion': {'electricity': 0, 'hydrogen': 1, 'gas': -1.45},
                                'EnergyNbhourCap': 0,  # used for hydroelectricity
                                'capacityLim': 100e3,'RampConstraintPlus':0.3
                                },
                               }
                         )
        )

        tech = "CCS1"
        capex, opex, LifeSpan = 100e3, 0e3, 60
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Carbon capture',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex,
                                'operationCost': opex, 'capacityLim': 100e3},
                               }
                         )
        )

        tech = "CCS2"
        capex, opex, LifeSpan = 100e3, 0e3, 60
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Carbon capture',
                                'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex,
                                'operationCost': opex, 'capacityLim': 100e3},
                               }
                         )
        )

        tech = "curtailment"
        capex, opex, LifeSpan = 0, 0, 100
        scenarioPACA['conversionTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'Category': 'Carbon capture',
                                'LifeSpan': LifeSpan, 'powerCost': 3000, 'investCost': capex,
                                'operationCost': opex, 'capacityLim': 100e3},
                               }
                         )
        )

scenarioPACA['conversionTechs'] = pd.concat(scenarioPACA['conversionTechs'], axis=1)

scenarioPACA['storageTechs'] = []
for k, year in enumerate(yearList[:-1]):
    tech = "Battery"
    capex1, opex1, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
        tech + ' - 1h', hyp='ref', year=year+yearStep/2)
    capex4, opex4, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
        tech + ' - 4h', hyp='ref', year=year+yearStep/2)
    capex_per_kWh = (capex4 - capex1) / 3
    capex_per_kW = capex1 - capex_per_kWh
scenarioPACA['storageTechs'] = []
for area in areaList:
    for k, year in enumerate(yearList[:-1]):
        tech = "Battery"
        capex1, opex1, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
            tech + ' - 1h', hyp='ref', year=year+yearStep/2)
        capex4, opex4, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(
            tech + ' - 4h', hyp='ref', year=year+yearStep/2)
        capex_per_kWh = (capex4 - capex1) / 3
        capex_per_kW = capex1 - capex_per_kWh

        scenarioPACA['storageTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year, 'storageResource': 'electricity',  # ambiguïté du nom des paramètres ?
                                'storageLifeSpan': LifeSpan,
                                'storagePowerCost': capex_per_kW,
                                'storageEnergyCost': capex_per_kWh,
                                # TODO: according to RTE OPEX seems to vary with energy rather than power
                                'storageOperationCost': opex1,
                                'p_max': 5000,
                                'c_max': 50000,
                                'storageChargeFactors': {'electricity': 0.9200},
                                'storageDischargeFactors': {'electricity': 1.09},
                                'storageDissipation': 0.0085,
                                },
                               }
                         )
        )

        tech = "Salt cavern"
        scenarioPACA['storageTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year,
                                'storageResource': 'hydrogen',
                                'storageLifeSpan': 40,
                                'storagePowerCost': 373e3*0.3,
                                'storageEnergyCost': 373e3*0.7,
                                'storageOperationCost': 15e3,
                                'p_max': 10000,
                                'c_max': stockage_h_area(area),
                                'storageChargeFactors': {'electricity': 0.0168, 'hydrogen': 1.0},
                                'storageDischargeFactors': {'hydrogen': 1.0},
                                'storageDissipation': 0,
                                },
                               }
                         )
        )

        tech = "H2 tank"
        scenarioPACA['storageTechs'].append(
            pd.DataFrame(data={tech:
                               {'AREA': area, 'YEAR': year,
                                'storageResource': 'hydrogen',
                                'storageLifeSpan': 20,
                                'storagePowerCost': 18e3*0.3,
                                'storageEnergyCost': 18e3*0.7,
                                'storageOperationCost': 2e3,
                                'p_max': 1000,
                                'c_max': 10000,
                                'storageChargeFactors': {'electricity': 0.0168, 'hydrogen': 1.0},
                                'storageDischargeFactors': {'hydrogen': 1.0},
                                'storageDissipation': 0,
                                },
                               }
                         )
        )


scenarioPACA['storageTechs'] = pd.concat(scenarioPACA['storageTechs'], axis=1)

scenarioPACA['transportTechs'] = []
for k, year in enumerate(yearList[:-1]):
    ttech = 'Pipeline_S'
    p_max = 50000.
    capex, opex, LifeSpan = 1583, 3e-4, 40
    scenarioPACA['transportTechs'].append(
        pd.DataFrame(data={ttech:
                           {'YEAR': year, 'transportResource': 'hydrogen',
                            'transportLifeSpan': LifeSpan, 'transportPowerCost': 9e-5, 'transportInvestCost': capex, 'transportOperationCost': opex,
                            # 'transportMinPower':1., 'transportMaxPower': p_max,
                            'transportEmissionCO2': 0,
                            'transportChargeFactors': {'hydrogen': 5e-3},
                            'transportDischargeFactors': {'hydrogen': 5e-3},
                            'transportDissipation': 2e-5,
                            # puissance maximale de fonctionnement du pipeline (=débit max), fixée
                            'transportUnitPower': 1 #tech_eco_data.p_max_fonc[ttech]
                            }
                           }
                     )
    )

    ttech = 'Pipeline_M'
    p_max = 50000.
    capex, opex, LifeSpan = 638, 1.2e-4, 40
    scenarioPACA['transportTechs'].append(
        pd.DataFrame(data={ttech:
                           {'YEAR': year, 'transportResource': 'hydrogen',
                            'transportLifeSpan': LifeSpan, 'transportPowerCost': 3.2e-4, 'transportInvestCost': capex, 'transportOperationCost': opex,
                            # 'transportMinPower':1., 'transportMaxPower': p_max,
                            'transportEmissionCO2': 0,
                            'transportChargeFactors': {'hydrogen': 5e-3},
                            'transportDischargeFactors': {'hydrogen': 5e-3},
                            'transportDissipation': 2e-5,
                            # puissance maximale de fonctionnement du pipeline (=débit max), fixée
                            'transportUnitPower':1 #tech_eco_data.p_max_fonc[ttech]
                            }
                           }
                     )
    )

    ttech = 'Pipeline_L'
    p_max = 50000.
    capex, opex, LifeSpan = 253, 3.4e-5, 40
    scenarioPACA['transportTechs'].append(
        pd.DataFrame(data={ttech:
                           {'YEAR': year, 'transportResource': 'hydrogen',
                            'transportLifeSpan': LifeSpan, 'transportPowerCost': 1.5e-3, 'transportInvestCost': capex, 'transportOperationCost': opex,
                            # 'transportMinPower':1., 'transportMaxPower': p_max,
                            'transportEmissionCO2': 0,
                            'transportChargeFactors': {'hydrogen': 5e-3},
                            'transportDischargeFactors': {'hydrogen': 5e-3},
                            'transportDissipation': 2e-5,
                            'transportUnitPower': 1 #tech_eco_data.p_max_fonc[ttech]
                            }
                           }
                     )
    )


# ttech = truck transporting hydrogen
for k, year in enumerate(yearList[:-1]):
    ttech = 'truckTransportingHydrogen'
    p_max = 50000  # to change
    capex, opex, LifeSpan = 296, 7e-3, 10
    scenarioPACA['transportTechs'].append(
        pd.DataFrame(data={ttech:
                           {'YEAR': year, 'transportResource': 'hydrogen',
                            'transportLifeSpan': LifeSpan, 'transportPowerCost': 4.2e-2, 'transportInvestCost': capex, 'transportOperationCost': opex,
                            # 'transportMinPower':1, 'transportMaxPower': p_max,
                            'transportEmissionCO2': 1/23,
                            'transportChargeFactors': {'hydrogen': 0.1},
                            'transportDischargeFactors': {'hydrogen': 0.001},
                            'transportDissipation': 0.0,
                            'transportUnitPower': 1
                            }
                           }
                     )
    )


# ttech = truck transporting electricity
# ttech = electric cable


scenarioPACA['transportTechs'] = pd.concat(scenarioPACA['transportTechs'], axis=1)

scenarioPACA['carbonTax'] = pd.DataFrame(data=np.linspace(0.0675, 0.165, nYears),
                                     index=yearList, columns=('carbonTax',))

scenarioPACA['carbonGoals'] = pd.DataFrame(data=np.linspace(974e6, 205e6, nYears),
                                       index=yearList, columns=('carbonGoals',))

scenarioPACA['maxBiogasCap'] = pd.DataFrame(data=np.linspace(0, 310e6, nYears),
                                        index=yearList, columns=('maxBiogasCap',))

scenarioPACA['gridConnection'] = pd.read_csv("Data/Raw/CalendrierHTB_courte_TIME.csv", sep=',', decimal='.', skiprows=0,
                                         comment="#").set_index(["TIMESTAMP"]).loc[t]
# print(scenarioPACA['gridConnection'])

scenarioPACA['economicParameters'] = pd.DataFrame({
    'discountRate': [0.04],
    'financeRate': [0.04]
}
)

# données des importations
df_res_ref = pd.read_csv('./Data/Raw/set2020-2050_horaire_TIMExRESxYEAR.csv',
                         sep=',', decimal='.', skiprows=0, comment="#").set_index(["YEAR", "TIMESTAMP", 'RESOURCES'])

t8760 = df_res_ref.index.get_level_values('TIMESTAMP').unique().values

# en €/MWh
# 4.5€ le kg d'H soit les 33*e-3 MWh donc 4.5/(33*e-3)€ le MWh
prix_kg = 100 # test
prix_MWh = prix_kg / (33 * 1e-3)

scenarioPACA['turpeFactorsHTB']=pd.DataFrame(columns=['HORAIRE','fixeTurpeHTB'],data={'P':5880,'HPH':5640,'HCH':5640,'HPE':5280,'HCE':4920}.items()).set_index('HORAIRE') # en €/MW/an part abonnement

df_elecPrice=pd.read_csv('./Data/Raw/marketPrice.csv').set_index(['YEAR_op','TIMESTAMP'])
df_elecCarbon=pd.read_csv('./Data/Raw/carbon.csv').set_index(['YEAR_op','TIMESTAMP'])
gasPriceFactor=[1,2,2,2]
bioGasPrice=[120,110,100,90]

scenarioPACA['resourceImportPrices'] = pd.concat(
    (
        pd.DataFrame(data={
            'AREA': area,
            'YEAR': year,
            'TIMESTAMP': t,
            'electricity': np.interp(t, t8760, df_elecPrice.loc[(year, slice(None)),'OldPrice_NonAct'].values),
            'natural gas': gasPriceFactor[k] * np.interp(t, t8760, df_res_ref.loc[(year, slice(None), 'gazNat'), 'importCost'].values),
            'biogas': bioGasPrice[k] * np.ones(nHours),
            'hydrogen': prix_MWh * np.ones(nHours),  # à changer
        }) for k, year in enumerate(yearList[1:])
        for area in areaList
    )
)

scenarioPACA['resourceImportCO2eq'] = pd.concat(
    (
        pd.DataFrame(data={
            'AREA': area,
            'YEAR': year,
            'TIMESTAMP': t,
            'electricity': np.interp(t, t8760, df_elecCarbon.loc[(year, slice(None)),'carbonContent'].values),
            # Taking 100 yr GWP of methane and 3% losses due to upstream leaks. Losses drop to zero in 2050.
            'gas': max(0, 0.03 * (1 - (year - yearZero)/(2050 - yearZero))) * 29 / 13.1 + 203.5 * (1 - tech_eco_data.get_biogas_share_in_network_RTE(year)),
            # Taking 100 yr GWP of methane and 3% losses due to upstream leaks. Losses drop to zero in 2050.
            'natural gas': max(0, 0.03 * (1 - (year - yearZero)/(2050 - yearZero))) * 29 / 13.1 + 203.5 * (1 - tech_eco_data.get_biogas_share_in_network_RTE(year)),
            'biogas': max(0, 0.03 * (1 - (year - yearZero)/(2050 - yearZero))) * 29 / 13.1,
            # Taking 100 yr GWP of H2 and 5% losses due to upstream leaks. Leaks fall to 2% in 2050 See: https://www.energypolicy.columbia.edu/research/commentary/hydrogen-leakage-potential-risk-hydrogen-economy
            'hydrogen': 0
            # max(0, 0.05 - .03 * (year - yearZero)/(2050 - yearZero)) * 11 / 33,
        }) for k, year in enumerate(yearList[1:])
        for area in areaList
    )
)

scenarioPACA['convTechList'] = ["Offshore wind - floating", "Onshore wind",
                            "Ground PV","ElectrolysisM","SMR", "Existing SMR", 'SMR + CCS1', 'SMR + CCS2']
ctechs = scenarioPACA['convTechList']
scenarioPACA['conversionTechs']=scenarioPACA['conversionTechs'][ctechs]
availabilityFactor = pd.read_csv('Data/Raw/availabilityFactor2020-2050_PACA_TIMExTECHxYEAR - renamed.csv',
                                 sep=',', decimal='.', skiprows=0).set_index(["YEAR", "TIMESTAMP", "TECHNOLOGIES"]).loc[(slice(None), t, slice(None))]
itechs = availabilityFactor.index.isin(ctechs, level=2)
scenarioPACA['availability'] = availabilityFactor.loc[(
    slice(None), slice(None), itechs)]

stechs=['Battery','H2 tank']
scenarioPACA['storageTechs']=scenarioPACA['storageTechs'][stechs]

# availability pour transport ?
ttechs_list = list(scenarioPACA['transportTechs'].columns.unique())

scenarioPACA["yearList"] = yearList
scenarioPACA["areaList"] = areaList
scenarioPACA["transitionFactors"] = pd.DataFrame(
    {'TECHNO1': ['Existing SMR', 'Existing SMR', 'SMR', 'SMR'],
     'TECHNO2': ['SMR + CCS1', 'SMR + CCS2', 'SMR + CCS1', 'SMR + CCS2'],
     'TransFactor': 1}).set_index(['TECHNO1', 'TECHNO2'])



# impBiogasCap=np.linspace(0, 5e6, nYears)
# # impH2Cap=np.linspace(0, 30e6, nYears)
# scenarioPACA['maxImportCap'] = pd.concat(
#     (
#         pd.DataFrame(index=[year],data={
#             'electricity': 10e10,
#             'gazNat': 10e10,
#             'gazBio': impBiogasCap[k+1],
#             'hydrogen': 0,
#             'gaz': 0
#         }) for k, year in enumerate(yearList[1:])
#     )
# )

# # expH2Cap=np.linspace(0, 30e6, nYears)
# scenarioPACA['maxExportCap'] = pd.concat(
#     (
#         pd.DataFrame(index=[year],data={
#             'electricity': 0,#10e6,
#             'gazNat': 0,
#             'gazBio': 0,
#             'hydrogen': 0,
#             'gaz': 0
#         }) for k, year in enumerate(yearList[1:])
#     )
# )
