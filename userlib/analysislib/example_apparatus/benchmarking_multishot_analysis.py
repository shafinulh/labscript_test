from lyse import *
from pylab import *
import matplotlib.pyplot as plt

df = data()

ramp_vf = df["ramp_vf"]

integrated_signal = df["benchmarking_single_shot_analysis", "ai1 integrated"]

plt.figure(figsize=(10, 6))

plt.plot(ramp_vf, integrated_signal)

plt.xlabel('final analog ramp voltgae')
plt.ylabel('Integrated Signal')
plt.title('Analog Ramp Voltage vs. Signal')
# plt.legend()
plt.grid(True)

plt.show()

# seq = Sequence(path, df)

