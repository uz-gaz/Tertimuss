import matplotlib.pyplot as plt
import numpy as np

x = [[1, 2, 3, 4, 5, 6, 7, 8, 10], [9, 8, 8, 8, 8, 6, 7, 8, 9]]

f, axarr = plt.subplots(2, sharex=True)
f.suptitle('CPU utilization')
axarr[0].plot(x[0], x[0])
axarr[1].plot(x[1], x[0])

#plt.plot(x[0])
#plt.plot(x[1])
#plt.show()
