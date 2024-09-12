import numpy as np
import matplotlib.pyplot as plt

# Parameters
m = 1.0        # Mass
hx = 1.0       # Rabi field
kT = 4.0       # Spin-dependent momentum shift

# Define the functions for energies
def h_eff(k):
    hz_k = k * kT / m  # SOC term
    return np.sqrt(hx**2 + hz_k**2)

def epsilon_k(k):
    kT2 = kT**2
    return (k**2 + kT2) / (2 * m)

def E_A(k):
    return epsilon_k(k) - h_eff(k)

def E_B(k):
    return epsilon_k(k) + h_eff(k)

# Range of k values
max_k = 10
k_values = np.linspace(-max_k, max_k, 400)

# Calculate energies
E_A_values = E_A(k_values)
E_B_values = E_B(k_values)

# Plot the energies
plt.figure(figsize=(4, 3))
plt.plot(k_values, E_A_values, label=r'$E_A(k)$')
plt.plot(k_values, E_B_values, label=r'$E_B(k)$')
plt.xlabel(r'$k$')
plt.ylabel(r'$E$')
# plt.title('Energies $E_A(k)$ and $E_B(k)$ as functions of $k$')
plt.legend()
plt.grid(False)
plt.tight_layout()
plt.savefig("media/energies.pdf")