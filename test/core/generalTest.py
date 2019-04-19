import matplotlib.pyplot as plt
import numpy as np

x = [200 * [1, 1, 1, 1, 1, 0, 0, 0, 0], 200 * [0, 0, 0, 0, 1, 1, 1, 1, 1], 200 * [1, 1, 1, 1, 1, 0, 0, 0, 0],
     200 * [0, 0, 0, 0, 1, 1, 1, 1, 1], 200 * [1, 1, 1, 1, 1, 0, 0, 0, 0], 200 * [0, 0, 0, 0, 1, 1, 1, 1, 1]]
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
f, axarr = plt.subplots(m, sharex=True)
f.suptitle('CPU utilization')
for i in range(m):
    for j in range(n):
        axarr[i].plot(i_tau_disc[i * n + j])
plt.show()


f, axarr = plt.subplots(m, sharex=True)
f.suptitle('CPU utilization')
for i in range(m):
    for j in range(n):
        axarr[i].plot(i_tau_disc[i * n + j])
plt.show()
