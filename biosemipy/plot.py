import matplotlib.pyplot as plt

for channel in a.data:
    plt.plot(channel[1:1000])
plt.show()