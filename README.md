# Simulation and Planning of HYdrogen Deployment and Evaluation at Regional Scale (SPHYDERS)

## Introduction 

## Files

`single-area-multi-period.py` is the main script, used to: 

- choose the output folder; 
- choose the scenario file; 
- choose the solver;
- build the model (function `systemModel`)  and solve it; 
- create the output folder and save the results. 

`tech_eco_data.py` is a techno-economical database for conversion and storage technologies, which can be used to build scenarios. 

`scenarios.py` defines a simulation scenario including:   

- `timeStep` defines the time step for the operation planning (given in hours)
- `areaList` the list of spatial nodes (*areas*)
- `yearZero` the start year for investment planning 
- `yearFinal` the final year for investment planning
- `yearStep` the investment planning period
- `dist` dictinary defining the distance (in km)  between spatial nodes 
- `scenario` is a dictionary containing `pandas` `DataFrames` defining the scenario

`f_multiResourceModelAna.py` file containing the `systemModel` functions which actually builds the model from the scenario dictionary. 

### Definition of scenario tables 

## Model description

### Sets 

| Set 		     | Index   | Description 							|
|----------------|---------|----------------------------------------|
| `TECHNOLOGIES` | `cT`    | Conversion technologies 				| 
| `TRANS_TECHNO` | `tT`    | Transport technologies  				| 
| `STOCK_TECHNO` | `sT`    | Storage technologies    				| 
| `RESOURCES`    | `r`     | Resources 			  					| 
| `AREA`         | `a`     | Spatial nodes 	      					|
| `TIMESTAMP`    | `t`     | Operation period time steps   			|
| `HORAIRE`      | `h`     | Subset of TIMESTEPS for network taxes 	|  
| `YEAR`         | `y`     | Target years 							|
| `YEAR_invest`  | `y_i`   | Investment periods 					| 
| `YEAR_op`      | `y_op`  | Operation periods 						|

### Parameters 

| Parameters    	  | Set indexes | Description 							 | Units |
|---------------------|-------------|----------------------------------------|-------|
| `areaConsumption`   |`y_op,t,r,a` | Final consumption of the resource at each time step of the year for the node  | MWh  |
| `availabilityFactor`|`y_op,t,cT,a`| Availability of a conversion tech. at each timestamp of the year for the area | n.d. |
| `conversionFactor`  |`r,cT`| Conversion factor of a resource for a given conversion tech. Positive for consumption| n.d. |
| `carbon_taxe`       |`y_op`| Carbon tax value | EUR/kgCO2 | 
| `gazBio_max`        |`y_op`| Maximum available quantitiy of biomethane | MWh | 
| `transFactor`       |`cT,cT`| Whether one technology can be converted to the other (boolean, 0 or 1) | n.d. | 
| `turpeFactors`      |`h`| Fixed component of the TURPE network tax related to connection power  | EUR/MW |
| `distances`         |`a,a`| Geographical distance between two nodes  | km | 
| `TechParameters` 	  |`cT,a,y_i`| Technical parameters for each conversion technology (dictionary) | - | 
| `ResourceParameters`|`y_op,t,r,a`| Parameters for each resource (dictionary) | - | 

### Conversion technology parameters 

| Technology Parameters     | Description 						   | Units |
|---------------------|----------------------------------------|-------|
| `EmissionCO2` | CO2 emissions for the technology when running |kgCO2/kgH2| 
| `investCost` | Fixed investment costs (CAPEX) |EUR/MW| 
| `operationCost` | Fixed operation costs (OPEX) |EUR/MW/yr| 
| `powerCost` | Variable costs |EUR/MWh|
| `lifespan` | Life span of a technology invested during the investment period |yr| 
| `maxCumulCapacity` | Maximum total number of units for the technology in the area |n.d.| 
| `maxInstallCapacity` | Maximum number of installed  unit during the investment period |n.d.| 
| `minCumulCapacity`   | Minimum total number of unit for the technology in the area |n.d.| 
| `minInstallCapacity` | Maximum number of installed  unit during the investment period  |n.d.| 
| `techUnitPower` | |MW|
| `RampConstraintPlus` | Ramp in % of the maximum power that can be increased during 1 time step |%|
| `RampConstraintMoins` | Ramp in % of the maximum power that can be cut during 1 time step |%|
| `yearStart` | Comissioning year for units reaching their end of life in the considered investment period |n.d.|

### Resource parameters 

| Resource Parameters     | Description 						   | Units |
|---------------------|----------------------------------------|-------|
|`importCost` | Import cost time series | EUR/MWh | 
|`importEmissionCO2` | CO2 emission factor time series | kgCO2/MWh| 

## To run 
## Changelog 
