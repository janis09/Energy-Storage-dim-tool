import math
import matplotlib.pyplot as plt

B=370.3
Ea=31700
z= 0.55
R=8.314
T=20+273.15
max_cycles = 1*62050+1
A = 0

#Case 1 DoD 0.25 and 0.67 C-rate
#Case 2 DoD 0.45 and C-rate 0.41
#Case 3 DoD 0.19 og C-rate 0.6
#Case 4 DoD 0.45 og C-rate 0.48

DoD = 0.19*2.2
cell_capacity = 2.2
ah_per_cycle = DoD*cell_capacity



c_rate = 0.6
Q_loss_end = 40

if c_rate >= 2:
    A = -47.836 * c_rate**3 + 1214.955*c_rate**2 - 9418.914*c_rate + 36041.6979 
else:
    A = 21681




Ah_loss = (Q_loss_end/(A *math.e**((-Ea+B*c_rate)/(R*T)) ))**(1/z)    

print("Ah at end of life: ", Ah_loss)

list_Q = []
list_N = []
cycles_per_year = 365*17
for x in range(max_cycles):
  
    ah = ah_per_cycle*(x+1)*2


    Q_loss_test = (A *math.e**((-Ea+B*c_rate)/(R*T)) )*(ah)**z
    list_Q.append(Q_loss_test)
    list_N.append(x)
    for y in range(10):
        if x == cycles_per_year*(1+y):
            print(str(Q_loss_test) + " : " + str(100-Q_loss_test))

    if Q_loss_test >= Q_loss_end:
        print("Cycles until end of life: "+ str(x))
        break

    

       
plt.xlabel("Charge/discharge cycles", fontsize = 16)
plt.ylabel("Capacity loss (%)", fontsize = 16)
plt.title('Semi-emperical model Cycling', fontsize = 18)
plt.grid(True)
plt.plot(list_N, list_Q)
#plt.legend(loc='upper left')
plt.show()
