import pybamm
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.optimize import curve_fit
start_time = time.time()
ambient_temp = 273.15 + 20
cycle_number = 10



model = pybamm.lithium_ion.DFN(
    {
        "SEI": "solvent-diffusion limited",
        "SEI porosity change": "true",
        "lithium plating": "partially reversible",
        "lithium plating porosity change": "true",  # alias for "SEI porosity change"
        "particle mechanics": ("swelling and cracking", "swelling only"),
        "SEI on cracks": "true",
        "loss of active material": "stress-driven",
        'calculate discharge energy': "true",
    }
)

param = pybamm.ParameterValues("OKane2022")

var_pts = {
    "x_n": 5,  # negative electrode
    "x_s": 5,  # separator
    "x_p": 5,  # positive electrode
    "r_n": 5,  # negative particle
    "r_p": 5,  # positive particle
}

param["Ambient temperature [K]"] = ambient_temp
ambient_temp = param["Ambient temperature [K]"]

init_temp = param["Initial temperature [K]"]
param["Initial temperature [K]"] = ambient_temp


exp = pybamm.Experiment(
    [
        
        "Charge at 0.3C until 4.1 V",
    ]
    + [
        (
            
            "Discharge at 0.2 C for 20 minutes",

            "Charge at 0.4C until 4.1 V",
            
            "Hold at 4.1 V until C/100",
        )
    ]
    * cycle_number
    
    
)
solver = pybamm.IDAKLUSolver()
sim = pybamm.Simulation(
    model, parameter_values=param, experiment=exp, solver=solver, var_pts=var_pts
)
sol = sim.solve()

end = time.time()
print("time: ", (end-start_time))
Qt = sol["Throughput capacity [A.h]"].entries
Q_SEI = sol["Loss of capacity to negative SEI [A.h]"].entries
Q_SEI_cr = sol["Loss of capacity to negative SEI on cracks [A.h]"].entries
Q_plating = sol["Loss of capacity to negative lithium plating [A.h]"].entries
Q_side = sol["Total capacity lost to side reactions [A.h]"].entries
Q_LLI = (
    sol["Total lithium lost [mol]"].entries * 96485.3 / 3600
)  # convert from mol to A.h


print(Qt[-1])
print(sol["Loss of lithium inventory [%]"].entries[-1])

DC = sol["Discharge capacity [A.h]"].entries
print("Discharge capacity [A.h]", DC[-1])

plt.figure()
plt.plot(Qt, Q_SEI, label="SEI", linestyle="dashed")
plt.plot(Qt, Q_SEI_cr, label="SEI on cracks", linestyle="dashdot")
plt.plot(Qt, Q_plating, label="Li plating", linestyle="dotted")
plt.plot(Qt, Q_side, label="All side reactions", linestyle=(0, (6, 1)))
plt.plot(Qt, Q_LLI, label="All LLI")
plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Capacity loss [A.h]")
plt.legend()
#plt.show()

plt.figure()
plt.plot(Qt, DC, label="Discharge cap")


Qt = sol["Throughput capacity [A.h]"].entries
LLI = sol["Loss of lithium inventory [%]"].entries
LAM_neg = sol["Loss of active material in negative electrode [%]"].entries
LAM_pos = sol["Loss of active material in positive electrode [%]"].entries
plt.figure()
plt.plot(Qt, LLI, label="LLI")
#plt.plot(Qt, LAM_neg, label="LAM (negative)")
#plt.plot(Qt, LAM_pos, label="LAM (positive)")
plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Degradation [%]")
plt.legend()
plt.show()



# Define the model that starts at y=0 when x=0
z = 0.46
def exp_zero_start(x, a, b):
    return a * (np.exp(-b) - 1)*x**(z + (3/(50)))

print(len(Qt))
# Step 3: Fit the model to data
params, _ = curve_fit(exp_zero_start, Qt[:12000], LLI[:12000], p0=(0.1, 1), maxfev=len(Qt))

a, b = params
print(f"Fitted equation: y = {a:.3f} * (e^({-b:.3f}) - 1) * x^{z:.3f}")

# Step 4: Plot the fit
x_fit = np.linspace(0, Qt[-1], 500)
y_fit = exp_zero_start(x_fit, *params)

plt.scatter(Qt, LLI, label='Data', color='blue')
plt.plot(x_fit, y_fit, label='Fitted Curve', color='red')
plt.title("Exponential Curve Fit")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.grid(True)
plt.show()
