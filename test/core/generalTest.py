# from core.task_generator import TaskGeneratorAlgorithm
# from core.task_generator.UUniFast import UUniFast

##tga: TaskGeneratorAlgorithm = UUniFast(12, 0.12)

# taskList: list = tga.generate()

# print(taskList)

import numpy as np
from scipy import linalg

b = np.array([[4, 5], [6, 7]])

#c = np.transpose(b)

c = b.T

print(b)
print(c)

print(c.dot(b))
