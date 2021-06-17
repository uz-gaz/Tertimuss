# Architecture of tertimuss

tertimuss has the following architecture: 

![Architecture of tertimuss](./diagrams/TertimussArchitecture.svg)


# Programming rules
Certain rules must be taken into account for the programing to avoid errors.
- No argument received can be modified unless the sole purpose of the function is to modify it. This allows arguments
  to be passed without making copies of them.