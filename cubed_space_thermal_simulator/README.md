**This module is in development yet**

# Cubed space thermal simulator

Note: 

## Definition
This module provides a thermal simulator for a mesh defined by cubes. The simulation is done using the unit edge cube as the minimal simulation unit.  
Each cube can be of a material in solid, liquid or gas state, however it assumes that state changes does not happens during the simulation.  
Also, the following heat transfer rules are followed:  

- Between two solid material cubes with a shared face only conduction happens
- Between two liquid/gas material cubes with a shared face 

It exposes the following functions  


## Functions
### cubedSpaceCreation(materialCubes: List[MaterialLocatedCube], cubeEdgeSize: float, environmentProperties: EnvironmentProperties, fixedEnergyApplicationPoints: Optional[List[EnergyLocatedCube]]) -> CubedSpace, List[int], List[int], List[int]  
This function create a cubedSpace  
Parameters definition
- materialLocatedCubes: List of cubes that conform the space. Each cube will have defined it's dimensions in unit units, the position in units and the thermal properties of the cube. 
- cubeEdgeSize: Cubes' edge size (each cube will have the same edge size)  
- environmentProperties: The material that will be surrounded the cube will have these properties. This material won't change him temperature, however it will affect to the mesh temperature.  
- fixedEnergyApplicationPoints: This parameter is only used with optimization purposes. If is not null, all of the elements of energyApplicationPoints in the function applyEnergy, must be in fixedEnergyApplicationPoints  

Return definition
- CubedSpace: Created mesh  
- List[int]: Id to refer to each material cube. It has the same size of materialCubes
- List[int]: Id to refer to each material cube. It has the same size of materialCubes
- List[int]: Id to refer to each material cube. It has the same size of materialCubes

### createSimulationState() -> SimulationState

### applyEnergy(cubeSpace: CubedSpace, energyApplicationPoints: List[EnergyLocatedCube], amountOfTime: float) -> CubedSpace
This function apply energy over the cubedSpace and return the transformed cubedSpace.
Parameters definition
- cubeSpace: Cube space to use.  
- energyApplicationPoints: Points where the energy is applied. If the list is empty, none energy will be applied, however the energy transfer between cubes will be simulated. Each cube will have defined it's dimensions in unit units, it's position in units and the amount of energy to be applied.  
- amountOfTime: Amount of time in seconds while the energy is being applied  

### obtainTemperature(cubeSpace: CubedSpace, surroundedCube: Optional[LocatedCube], units: ThermalUnits): ModelTemperatureArray
This function return the temperature in each cube of unit edge that conform the cubedSpace
Parameters definition
- cubeSpace: Cube space to use.  
- surroundedCube: Only the temperature of the elements in this surrounded cube will be returned. By default, this cube is calculated as the cube that surrounds the rest of the cubes.  
- units: Units to receive the temperature.  

## References:
For the thermal simulation is used the model proposed by:
- Desirena, Gaddiel & Vazquez, Carlos & Ramirez-Trevino, Antonio & Gomez-Gutierrez, David. (2014). Thermal modelling for temperature control in MPSoC's using Timed Continuous Petri Nets. 2014 IEEE Conference on Control Applications, CCA 2014. 2135-2140. 10.1109/CCA.2014.6981618. 

## TODOLIST: 
- Simulate conduction (only with mesh)
- Create visualization
- Simulate convection (only with environment)
- Simulate fluids