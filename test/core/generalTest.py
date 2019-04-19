import matplotlib.pyplot as plt
import numpy as np

x = [[1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0, 0, 0],
     [0, 0, 0, 0, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1]]
x = np.asarray(x)

# f, axarr = plt.subplots(2, sharex=True)
# f.suptitle('CPU utilization')
# axarr[0].plot(x[0])
# axarr[1].plot(x[1])

# plt.plot(x[0])
# plt.plot(x[1])
# plt.show()

# TODO: Revisar esto
i_tau_disc = x
n = 3
m = 2

f, axarr = plt.subplots(m, num="titulo de prueba")
#f.figure(num="titulo de prueba")
f.suptitle('CPU utilization')
for i in range(m):
    for j in range(n):
        axarr[i].plot(i_tau_disc[i * n + j], label="CPU " + str(m))
    axarr[i].legend(loc='upper left')
plt.show()
