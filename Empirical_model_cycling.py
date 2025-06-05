import math
import matplotlib.pyplot as plt

B=370.3
Ea=31700
z= 0.55
R=8.314
T=20+273.15
max_cycles = 100000

DoD = 0.2
cell_capacity = 2.2
ah_per_cycle = DoD*cell_capacity


A = 0
c_rate = 0.5
Q_loss_end = 20

if c_rate >= 2:
    A = -47.836 * c_rate**3 + 1214.955*c_rate**2 - 9418.914*c_rate + 36041.6979 
else:
    A = 21681




Ah_loss = (Q_loss_end/(A *math.e**((-Ea+B*c_rate)/(R*T)) ))**(1/z)    

print("Ah at end of life: ", Ah_loss)

list_Q = []
list_N = []

for x in range(max_cycles):
  
    ah = ah_per_cycle*(x+1)*2


    Q_loss_test = (21681 *math.e**((-Ea+B*2)/(R*T)) )*(ah)**z
    list_Q.append(Q_loss_test)
    list_N.append(x)
    
    if Q_loss_test >= Q_loss_end:
        print("Cycles until end of life: "+ str(x))
        break
    
plt.xlabel("Charge/discharge cycles")
plt.ylabel("Capacity loss (%)")
plt.grid(True)
plt.plot(list_N, list_Q)
plt.show()