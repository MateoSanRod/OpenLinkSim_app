import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root


def find_nonlinear_solutions(a, b, c, d, q, n_initial=8):
    def equations(x):
        psi1, psi2 = x
        eq1 = a * np.cos(q) + b * np.cos(psi1) - (d + c * np.cos(psi2))
        eq2 = a * np.sin(q) + b * np.sin(psi1) - (c * np.sin(psi2))
        return [eq1, eq2]

    # grid of initial guesses
    theta_vals = np.linspace(0, 2 * np.pi, n_initial, endpoint=False)
    roots = []
    for th1 in theta_vals:
        for th2 in theta_vals:
            sol = root(equations, [th1, th2], jac=False)
            if sol.success:
                p1, p2 = sol.x % (2 * np.pi)
                roots.append((p1, p2))

    # deduplicate within tolerance
    unique = []
    for p1, p2 in roots:
        if not any(np.hypot(p1 - u1, p2 - u2) < 1e-3 for u1, u2 in unique):
            unique.append((p1, p2))

    return np.array(unique)


# Barker four-bar classifications with example link lengths (a, b, c, d)
configurations = {
    "GCCC": (2.5, 2, 2, 1),
    "GCRR": (1, 2.5, 2, 2),
    "GRCR": (2, 1, 2, 2.5),
    "GRRC": (2.5, 2, 1, 2),
    "RRR1": (1, 2, 2, 4.5),
    "RRR2": (4.5, 2, 2, 1),
    "RRR3": (2, 4.5, 2, 1),
    "RRR4": (1, 2, 4.5, 2),
    "SCCC": (2, 1.5, 1.5, 1),
    "SCRR": (1, 1.5, 1.5, 2),
    "SRCR": (1.5, 1, 1.5, 2),
    "SRRC": (2, 1.5, 1, 1.5),
    "S2X": (3, 1, 3, 1),
    "S3X": (2, 2, 2, 2),
}

# Sampling settings
q_values = np.linspace(0, 2 * np.pi, 1000)
ticks = np.linspace(0, 2 * np.pi, 9)
tick_labels = [
    r'$0$', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$', r'$\frac{3\pi}{4}$',
    r'$\pi$', r'$\frac{5\pi}{4}$', r'$\frac{3\pi}{2}$', r'$\frac{7\pi}{4}$',
    r'$2\pi$'
]

# Math styling
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.rm'] = 'Times New Roman'
plt.rcParams['mathtext.it'] = 'Times New Roman'
plt.rcParams['mathtext.bf'] = 'Times New Roman'
plt.rcParams['mathtext.sf'] = 'Times New Roman'

# Create 7×2 grid of subplots
fact = 1.1
fig, axes = plt.subplots(7, 2, figsize=(14*fact, 19*fact))
axes = axes.flatten()

for idx,(ax, (case, (a, b, c, d))) in enumerate(zip(axes, configurations.items())):
    q_list, psi1_list, psi2_list = [], [], []
    for q in q_values:
        sols = find_nonlinear_solutions(a, b, c, d, q)
        for psi1, psi2 in sols:
            q_list.append(q)
            psi1_list.append(psi1)
            psi2_list.append(psi2)

    # Scatter plots
    ax.scatter(q_list, psi1_list, s=3, label=r'$\psi_1$', color='tab:blue', alpha=0.5)
    ax.scatter(q_list, psi2_list, s=3, label=r'$\psi_2$', color='tab:green', alpha=0.5)

    # Axis ticks and labels
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    ax.set_yticks(ticks)
    ax.set_yticklabels(tick_labels)
    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(0, 2 * np.pi)

    ax.set_xlabel(r'$q$ [rad]')
    ax.set_ylabel(r'$\psi_1$ & $\psi_1$ [rad]')

    ax.set_title(f'{idx+1} - Case {case}\t' + r'($r_{1}$, $r_{2}$, $r_{3}$, $r_{4}$ '+ f'= {a}, {b}, {c}, {d})', fontsize=12)

plt.tight_layout()
plt.subplots_adjust(top=0.95)

fig.suptitle(r'$\psi_1$ and $\psi_2$ vs $q$ for Barker Four-Bar Classes', fontsize=18)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels ,loc='lower center', fontsize='x-large', bbox_to_anchor=(0.5, -0.0005),
           ncol=2,markerscale=4)
plt.tight_layout(rect=[-0.01, 0.02, 1.01, 0.99])
plt.savefig('Solutions for psi_1 and psi_2 vs q.png', dpi=400)
# plt.show()


