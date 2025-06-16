import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.interpolate import interp1d
# Define the function

cycles = 7300
ah_per_cycle = 2.25

#Values from fitting model
a =0.046 
b = 0.675
z = 0.47

list_Q = []
list_N = []

for x in range(int(cycles*ah_per_cycle*2)):

    Q_loss_test =1* (np.exp(b) - 1)*x**z
    list_Q.append(Q_loss_test)
    list_N.append(x)
    

x1 = np.linspace(0, 10, len(list_Q))

q_cal_list = []
for x in range(365*3*10):
    q_loss = 165000*np.exp(-4180/(273.15+20)) *np.exp(0.01*0.5)*x**0.5
    q_cal_list.append(q_loss)
    
x2 = np.linspace(0, 10, len(q_cal_list))

# Generate x values (for example, from 0 to 10)
#Transform fitting curve loss with Ah-throughput to per year. 
interp_func = interp1d(x2, q_cal_list, kind='linear')
data2_resampled = interp_func(x1)
combined = list_Q + data2_resampled


# Plotting
plt.figure(figsize=(8, 6))
plt.plot(x1,list_Q, label="Cycling loss", linestyle='dashed')
plt.plot(x1,data2_resampled, label="Calendar loss",linestyle='--')
plt.plot(x1,combined, label="Combined loss")
plt.xlabel("Years", fontsize = 16)
plt.ylabel("Capacity loss (%)", fontsize = 16)
plt.title('Capacity loss Combined Physical- and Calendar-model', fontsize = 18)
plt.legend(fontsize=14)
plt.grid(True)
plt.show()
