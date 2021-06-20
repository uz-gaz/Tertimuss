# Architecture of tertimuss
## Class diagrams
The package architecture of tertimuss is defined in the following UML diagram:

![Architecture of tertimuss](./diagrams/TertimussArchitecture.svg)

In the following diagrams define the architecture of the different packages.

### TCPN simulator
![TCPN simulator](./diagrams/tcpn_simulator_class_diagram.svg)

### Cubed space thermal simulator
![Cubed space thermal simulator](./diagrams/cubed_space_simulator.svg)

### Scheduler simulation library
![Scheduler simulation library](./diagrams/SimulationLIbArchitecture.svg)

### Task generation algorithms
![Task generation algorithms](./diagrams/TaskGeneratorClassDiagram.svg)

### Scheduler pack
![Scheduler pack](./diagrams/schedulers.svg)

## Simulation components
The following figure represents the architecture of tertimuss in execution time.
![Simulation components](./diagrams/ComponentesTertimuss.svg)

# Programming rules
Certain rules must be taken into account for the programing to avoid errors.
- No argument received can be modified unless the sole purpose of the function is to modify it. This allows arguments
  to be passed without making copies of them.