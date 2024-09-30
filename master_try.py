import numpy as np
from qutip import *
import matplotlib.pyplot as plt

# Parameters for the system
hbar = 1  # Planck's constant (setting hbar = 1 for simplicity)
g = 1.0  # Atom-cavity coupling strength
Delta = 1.0  # Detuning
kappa = 0.5  # Cavity decay rate
gamma_feedback = 0.2  # Feedback cooling rate
num_cav_levels = 10  # Number of cavity levels
num_atom_levels = 2  # Atom levels (ground and excited)

# Define operators
a = tensor(destroy(num_cav_levels), qeye(num_atom_levels))  # Cavity annihilation operator
sigma_minus = tensor(qeye(num_cav_levels), destroy(num_atom_levels))  # Atom lowering operator
sigma_plus = sigma_minus.dag()  # Atom raising operator

# Hamiltonian for cavity cooling
H_cavity = hbar * Delta * a.dag() * a + hbar * g * (a.dag() * sigma_minus + a * sigma_plus)

# Lindblad operator for cavity photon emission
L_cavity = np.sqrt(kappa) * a

# Define feedback Hamiltonian (force applied based on measurement)
def feedback_hamiltonian(x):
    return hbar * gamma_feedback * x * (a.dag() * a)

# Define the system's master equation
def master_equation(rho, t, H, L_list):
    # Unitary evolution
    d_rho = -1j / hbar * (H * rho - rho * H.dag())
    
    # Dissipative evolution (Lindblad terms)
    for L in L_list:
        d_rho += L * rho * L.dag() - 0.5 * (L.dag() * L * rho + rho * L.dag() * L)
    
    return d_rho

# Initial state: cavity in vacuum state, atom in the excited state
psi0 = tensor(basis(num_cav_levels, 0), basis(num_atom_levels, 1))  # Start with atom excited
rho0 = psi0 * psi0.dag()

# Time array for evolution (increase time for better dynamics)
tlist = np.linspace(0, 20, 1000)

# Define quantum jump evolution function
def quantum_jump_evolution(H, L_list, psi0, tlist):
    result = mcsolve(H, psi0, tlist, L_list, [])
    return result

# Function to extract final kinetic energy (velocity related)
def final_velocity(photon_numbers, tlist):
    # Assuming final velocity is related to the final photon number at the last time point
    return photon_numbers[-1]

# Function to run cooling simulation for a method
def run_cooling_simulation(H_cooling, L_list, psi0, tlist, feedback=False):
    if feedback:
        for t in tlist:
            x = np.random.randn()  # Random feedback measurement outcome
            H_feedback = feedback_hamiltonian(x)
            H_cooling += H_feedback

    result = quantum_jump_evolution(H_cooling, L_list, psi0, tlist)
    return result

# Function to calculate photon number evolution
def calculate_photon_number_evolution(a, result):
    photon_numbers = expect(a.dag() * a, result.states)
    return photon_numbers

# Run for Cavity Cooling
results_cavity = run_cooling_simulation(H_cavity, [L_cavity], psi0, tlist)
photon_numbers_cavity = calculate_photon_number_evolution(a, results_cavity)
final_velocity_cavity = final_velocity(photon_numbers_cavity, tlist)

# Run for Feedback Cooling
results_feedback = run_cooling_simulation(H_cavity, [L_cavity], psi0, tlist, feedback=True)
photon_numbers_feedback = calculate_photon_number_evolution(a, results_feedback)
final_velocity_feedback = final_velocity(photon_numbers_feedback, tlist)

# Run for Combined Cooling
results_combined = run_cooling_simulation(H_cavity, [L_cavity], psi0, tlist, feedback=True)
photon_numbers_combined = calculate_photon_number_evolution(a, results_combined)
final_velocity_combined = final_velocity(photon_numbers_combined, tlist)

# Plot the results
plt.figure(figsize=(10, 6))

# Plot photon number evolution for all methods
plt.plot(tlist, photon_numbers_cavity, label="Cavity Cooling")
plt.plot(tlist, photon_numbers_feedback, label="Feedback Cooling")
plt.plot(tlist, photon_numbers_combined, label="Combined Cooling")

plt.xlabel('Time')
plt.ylabel('Photon Number (related to energy/velocity)')
plt.title('Cooling Dynamics Comparison')
plt.legend()
plt.grid(True)

# Display the plot
plt.show()

# Print final photon numbers (related to the final energy/velocity)
print(f"Final Velocity (Photon Number) with Cavity Cooling: {final_velocity_cavity}")
print(f"Final Velocity (Photon Number) with Feedback Cooling: {final_velocity_feedback}")
print(f"Final Velocity (Photon Number) with Combined Cooling: {final_velocity_combined}")
