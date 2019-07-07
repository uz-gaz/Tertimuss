import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    fig, ax = plt.subplots()



    ax.bar([1],[1], align='center', label="Execution")
    ax.legend(loc='best')
    # ax.xticks(y_pos, objects)
    # ax.ylabel('Usage')
    #ax.title('Programming language usage')

    plt.show()
