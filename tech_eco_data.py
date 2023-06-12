from scipy.interpolate import interp1d
import numpy as np

#############################
# PROPRIETES TECHNOLOGIQUES #
#############################
# un effort est fait pour reprendre les données choisies dans les scénarios du groupe infrastructure
# capex, opex, lifespan ne sont pas changés et restent déterminés par electrolyser_capex_Reksten2022

# on distingue la puissance de consommation et de production

# propriétés électrolyseurs
# facteur conversion électricité -> hydrogène
conv_el_h = 0.65
# hydrogène produit par électrolyseur de taille S (en MW), selon scénario 1
# (1MW de conso électrique pour 18kg/h ~ 600kW d'hydrogène produit)
power_S = 600e-3  # MW

# liste des puissances max de ressources
# - pour une tech : produites par une installation (en MW)
# - pour une ttech : transportables par km (en MW/km)
p_max_fonc = {
    "Offshore wind - floating": 12,
    "Onshore wind": 6,
    "Ground PV": 3*10**(-3), # Installation minimum : 3 kWc
    "ElectrolysisS": power_S,
    "ElectrolysisM": 10 * power_S,
    "ElectrolysisL": 100 * power_S,
    # puissance maximale de fonctionnement du pipeline (=débit max), fixée
    "Pipeline_S": 100,
    "Pipeline_M": 1000,
    "Pipeline_L": 10000,
    # capacité d'un camion : C = 600kg = 600*33 = 19800 kWh = 19.8 MWh
    # c'est aussi la qté d'hydrogène qu'un camion transport en 1 heure sur 1 km
    "truckTransportingHydrogen": 19.8
}


def get_biogas_share_in_network_RTE(year):
    # [.001, .11, .37, 1])
    return np.interp(year, [2019, 2030, 2040, 2050], [0] * 4)


def get_capex_new_tech_RTE(tech, hyp='ref', year=2020, var=None):
    # https://assets.rte-france.com/prod/public/2022-06/FE2050%20_Rapport%20complet_ANNEXES.pdf page 937
    years = [2020, 2030, 2040, 2050, 2060]

    if tech == "Offshore wind - floating":
        capex = {
            'ref':  interp1d(years, [3100, 2500, 2200, 1900, 1900], fill_value=(3100, 1900), bounds_error=False),
            'low':  interp1d(years, [3100, 2100, 1700, 1300, 1300], fill_value=(3100, 1300), bounds_error=False),
            'high': interp1d(years, [3100, 2900, 2700, 2500, 2500], fill_value=(3100, 2500), bounds_error=False),
        }
        opex = {
            'high': interp1d(years, [110, 90, 80, 70, 70], fill_value=(110, 70), bounds_error=False),
            'low': interp1d(years,  [110, 75, 50, 40, 40], fill_value=(110, 40), bounds_error=False),
            'ref': interp1d(years,  [110, 80, 60, 50, 50], fill_value=(100, 50), bounds_error=False),
        }
        life = {
            'high':  interp1d(years, [20, 25, 30, 40, 40], fill_value=(20, 40), bounds_error=False),
            'low':  interp1d(years, [20, 25, 30, 40, 40], fill_value=(20, 40), bounds_error=False),
            'ref':  interp1d(years, [20, 25, 30, 40, 40], fill_value=(20, 40), bounds_error=False),
        }

    elif tech == "Onshore wind":
        capex = {
            'ref':  interp1d(years, [1300, 1200, 1050, 900, 900], fill_value=(1300, 900), bounds_error=False),
            'low':  interp1d(years, [1300, 710, 620, 530, 530], fill_value=(1300, 530), bounds_error=False),
            'high': interp1d(years, [1300, 1300, 1300, 1300, 1300], fill_value=(1300, 1300), bounds_error=False),
        }
        opex = {
            'high': interp1d(years, [40, 40, 40, 40, 40], fill_value=(40, 40), bounds_error=False),
            'low': interp1d(years,  [40, 22, 18, 16, 16], fill_value=(40, 16), bounds_error=False),
            'ref': interp1d(years,  [40, 35, 30, 25, 25], fill_value=(40, 25), bounds_error=False),
        }
        life = {
            'high':  interp1d(years, [25, 30, 30, 30, 30], fill_value=(25, 30), bounds_error=False),
            'low':  interp1d(years, [25, 30, 30, 30, 30], fill_value=(25, 30), bounds_error=False),
            'ref':  interp1d(years, [25, 30, 30, 30, 30], fill_value=(25, 30), bounds_error=False),
        }

    elif tech == "Ground PV":
        capex = {
            'ref':  interp1d(years, [747, 597, 517, 477, 477], fill_value=(747, 477), bounds_error=False),
            'low':  interp1d(years, [747, 557, 497, 427, 427], fill_value=(747, 427), bounds_error=False),
            'high': interp1d(years, [747, 612, 562, 527, 527], fill_value=(747, 527), bounds_error=False),
        }
        opex = {
            'high': interp1d(years, [11, 10, 10, 9, 9], fill_value=(11, 9), bounds_error=False),
            'low': interp1d(years,  [11, 9, 8, 7, 7], fill_value=(11, 7), bounds_error=False),
            'ref': interp1d(years,  [11, 10, 9, 8, 8], fill_value=(11, 8), bounds_error=False),
        }
        life = {
            'high':  interp1d(years, [25, 30, 30, 30, 30], fill_value=(25, 30), bounds_error=False),
            'low':  interp1d(years, [25, 30, 30, 30, 30], fill_value=(25, 30), bounds_error=False),
            'ref':  interp1d(years, [25, 30, 30, 30, 30], fill_value=(25, 30), bounds_error=False),
        }

    # modification des puissances p_max_fonc selon les données de scenarios.py
    # comme Pel est ici la puissance électrique consommée, on divise par le facteur de conversion élec->H


    elif tech == "ElectrolysisS":
        capex = {
            'ref':  interp1d(years, electrolyser_capex_Reksten2022(tech='Alkaline', Pel=p_max_fonc[tech] / conv_el_h, year=np.array(years)),
                              fill_value=(electrolyser_capex_Reksten2022('Alkaline', Pel=p_max_fonc[tech] , year=2020), electrolyser_capex_Reksten2022('Alkaline', Pel=p_max_fonc[tech] , year=2050)), bounds_error=False),
        }
        opex = {
            'ref': interp1d(years, [12] * 5, fill_value=(12, 12), bounds_error=False),
        }
        life = {
            'ref':  interp1d(years, [30] * 5, fill_value=(30, 30), bounds_error=False),
        }

    elif tech == "ElectrolysisM":
        capex = {
            'ref':  interp1d(years, electrolyser_capex_Reksten2022(tech='Alkaline', Pel=p_max_fonc[tech] / conv_el_h, year=np.array(years)),
                             fill_value=(electrolyser_capex_Reksten2022('Alkaline', Pel=p_max_fonc[tech] , year=2020), electrolyser_capex_Reksten2022('Alkaline', Pel=p_max_fonc[tech] , year=2050)), bounds_error=False),
        }
        opex = {
            'ref': interp1d(years, [12] * 5, fill_value=(12, 12), bounds_error=False),
        }
        life = {
            'ref':  interp1d(years, [30] * 5, fill_value=(30, 30), bounds_error=False),
        }

    elif tech == "ElectrolysisL":
        capex = {
            'ref':  interp1d(
                years,
                electrolyser_capex_Reksten2022(
                    tech='Alkaline',
                    Pel=p_max_fonc[tech] / conv_el_h,
                    year=np.array(years))
                ,fill_value=(electrolyser_capex_Reksten2022('Alkaline', Pel=p_max_fonc[tech] , year=2020), electrolyser_capex_Reksten2022('Alkaline', Pel=p_max_fonc[tech] , year=2050)), bounds_error=False
            ),
        }
        opex = {
            'ref': interp1d(years, [12] * 5, fill_value=(12, 12), bounds_error=False),
        }
        life = {
            'ref':  interp1d(years, [30] * 5, fill_value=(30, 30), bounds_error=False),
        }

    elif tech == 'Battery - 1h':
        capex = {
            'ref':  interp1d(years, [537, 406, 332, 315, 315], fill_value=(537, 315), bounds_error=False),  # EUR/kW
        }

        opex = {
            'ref':  interp1d(years, [11] * 5, fill_value=(11, 11), bounds_error=False),  # EUR/kW/yr
        }
        life = {
            'ref':  interp1d(years, [15] * 5, fill_value=(15, 15), bounds_error=False),
        }

    elif tech == 'Battery - 4h':
        capex = {
            'ref':  interp1d(years, [1480, 1101, 855, 740, 740], fill_value=(1480, 740), bounds_error=False),  # EUR/kW
        }

        opex = {
            'ref':  interp1d(years, [30] * 5, fill_value=(30, 30), bounds_error=False),  # EUR/kW/yr
        }
        life = {
            'ref':  interp1d(years, [15] * 5, fill_value=(15, 15), bounds_error=False),
        }


    if var == "capex":
        return 1e3 * capex[hyp](year)
    elif var == "opex":
        return 1e3 * opex[hyp](year)
    elif var == 'lifetime':
        return life[hyp](year)
    else:
        return 1e3 * capex[hyp](year), 1e3 * opex[hyp](year), float(life[hyp](year))


def electrolyser_capex_Reksten2022(tech, Pel, year=2020):
    '''
    Reference: Reksten et al. (2022) https://www.sciencedirect.com/science/article/pii/S0360319922040253

        Pel: electrolyser electrical power consumption (MW)
    tech: electrolyser technology
    year: installation year 
    '''
    # conversion des MW en kW, unité dans laquelle la formule est écrite
    pel_kW = Pel * 1.e3

    if tech == 'PEM':
        alpha, beta, k0, k = 0.622, -158.9, 585.85, 9458.2
    elif tech == 'Alkaline':
        alpha, beta, k0, k = 0.649, -27.33, 301.04, 11603

    return (k0 + k/pel_kW * pel_kW**alpha) * (year/2020) ** beta


# capex/kW pour electrolyseur S en 2050 = 748.70€
# M : 654€
# L : 614.41€