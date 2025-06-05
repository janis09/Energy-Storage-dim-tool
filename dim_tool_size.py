import numpy as np
import matplotlib.pyplot as plt

def calculate_battery_pack(time_hours, power_kw ,cell_capacity_ah, cell_nominal_voltage_v, DoD, SoC_start, voltage_high_cutoff, voltage_low_cutoff, EOL_capacity_loss, SoC_high_cutoff, SoC_low_cutoff):
    """
    Calculate battery sizing and pack configuration based on a load profile and cell specifications.
    
    Parameters:
    -Explanation
    
    Returns:
    - Results...
    """
    
    
    # Calculate energy consumption
    energy = 0
    for x in range(len(power_kw)):
        energy += power_kw[x]
        
    energy_required_kwh = energy/60

    power_w = power_kw * 1000  # Convert kW to W
    current_a = power_w / voltage_v  # Current in A - strøm som må trekkes per tids enhet
    peak_current_a = np.max(current_a) # Finner peak current

    # Required battery capacity in Ah
    battery_capacity_ah = (energy_required_kwh * 1000) / voltage_v  # Energy (Wh) / Voltage (V) - Finner hvor mange Ah batteriet må være, Wh/V = Ah

    recommended_battery_capacity_ah_BOL = battery_capacity_ah / (DoD) #* safety_margin # Antar tap på 20%, hvor mye kWh må det være for å håndtere det. 
    recommended_battery_capacity_ah_EOL = recommended_battery_capacity_ah_BOL/(1-EOL_capacity_loss)
    # Battery pack design
    soc_values = np.linspace(SoC_low_cutoff*100,SoC_high_cutoff*100, len(power_kw) )
    #list(range(int(SoC_low_cutoff*100), int(SoC_high_cutoff*100+1)))
    voltage_values = np.linspace(voltage_low_cutoff, voltage_high_cutoff, len(power_kw))
    SoC_end = (SoC_start - DoD)*100
    
    mask = (soc_values <= SoC_start*100) & (soc_values >= SoC_end)
    voltage_mask = voltage_values[mask]
    
    v_max = np.max(voltage_mask)
    v_min = np.min(voltage_mask)
    v_avg = np.mean(voltage_mask)
    
    
    n_series = int(np.ceil(voltage_v / v_avg)) # Finner antall batteri celler i serie, for å oppnå riktig spenning. 
    n_parallel = int(np.ceil(recommended_battery_capacity_ah_BOL / cell_capacity_ah)) # Finner antall batteri pakker i parallell, for å oppnå riktig voltage
    total_cells = n_series * n_parallel # Antall batteri celler
    
    i_max = 1000*power_kw[0]/voltage_v
    i_avg = 0
    i_min = 1000*power_kw[0]/voltage_v
    
    avg_c_rate = 0
    min_c_rate = i_min/recommended_battery_capacity_ah_BOL
    max_c_rate = i_max/recommended_battery_capacity_ah_EOL
    
    for x in range(len(power_kw)):

        if (1000*power_kw[x]/voltage_v) >= i_max:
            i_max = 1000*power_kw[x]/voltage_v
            max_c_rate = i_max/recommended_battery_capacity_ah_EOL
            
        if (1000*power_kw[x]/voltage_v) <= i_min:
            i_min = 1000*power_kw[x]/voltage_v
            min_c_rate = i_min/recommended_battery_capacity_ah_BOL
            
        i_avg += power_kw[x]/voltage_v
        
    i_avg =1000* i_avg/len(power_kw)
    avg_c_rate = i_avg/((recommended_battery_capacity_ah_BOL+recommended_battery_capacity_ah_EOL)/2)
    
    results = {
        'Total energy per cycle [kWh]]': energy_required_kwh,
        'Battery size at end of life [Ah]' : recommended_battery_capacity_ah_EOL,
        'Battery size at start of life [Ah]': recommended_battery_capacity_ah_BOL,
        'Number of Cells in Series': n_series,
        'Number of Cells in Parallel': n_parallel,
        'Total_Cells': total_cells,
        'Max battery voltage': v_max * n_series,
        'Min battery voltage': v_min * n_series,
        'Max cell voltage': v_max,
        'Min cell voltage': v_min,
        'Max battery current': i_max,
        'Min battery current': i_min,
        'Average battery current': i_avg,
        'Max C-rate during lifetime': max_c_rate,
        'Min C-rate during lifetime': min_c_rate,
        'Average C-rate during lifetime': avg_c_rate

    }

    return results, time_hours, power_kw, current_a

def plot_load_profile(time_hours, power_kw, current_a):
    """Plot the load profile and current over time."""
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Power (kW)', color=color)
    ax1.plot(time_hours, power_kw, marker='o', color=color, label='Power (kW)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Current (A)', color=color)
    ax2.plot(time_hours, current_a, marker='x', linestyle='--', color=color, label='Current (A)')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Load Profile and Current Over Time')
    fig.tight_layout()
    #plt.show()

if __name__ == "__main__":
    
    # Create load profile: 20 minutes at 400 kW
    time_minutes = np.arange(0, 20, 1)  # from 0 to 20 minutes, step 1 min
    time_hours = time_minutes / 60.0  # convert to hours
    power_kw = np.full_like(time_hours, 525.0)  # constant 525 kW load

    # Voltage used for load
    voltage_v = 1000
    
    # SoC the batteries start at
    SoC_start = 0.8 #1 is at high voltage cutoff, 0 is at low voltage cutoff
    
    # The Depth of Discharge of the battery
    DoD = 0.2
    
    # Cell specifications
    cell_capacity_ah = 2.5  # Capacity of one cell (Ah)
    cell_nominal_voltage_v = 3.7  # Nominal voltage of one cell (V)
    cell_max_current_a = 5  # Maximum current per cell (A)

    voltage_high_cutoff = 3.3 #Voltage at 80% SoC
    voltage_low_cutoff = 3.2 #Voltage at 20% SoC

    SoC_high_cutoff = 0.8
    SoC_low_cutoff = 0.2

    EOL_capacity_loss = 0.2 #Loss of capacity at end of life

    # Calculate battery pack
    results, time_hours, power_kw, current_a = calculate_battery_pack(time_hours, power_kw ,cell_capacity_ah, voltage_v, DoD,
                                                                      SoC_start, voltage_high_cutoff, voltage_low_cutoff, 
                                                                      EOL_capacity_loss, SoC_high_cutoff, SoC_low_cutoff)

    # Display results
    print("Battery Pack Design Results:")
    for key, value in results.items():
        print(f"{key}: {value:.2f}")

    # Plot load profile
    #plot_load_profile(time_hours, power_kw, current_a)
