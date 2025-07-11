import matplotlib.pyplot as plt


def get_success_rate(filename):
    with open(f"out/{filename}", "r") as f:
        lines = f.readlines()

    total = len(lines)
    successes = sum(1 for line in lines if line.strip() == "Success")

    success_rate = successes / total if total > 0 else 0
    return success_rate


fmlp_successes = []
pip_successes = []
for i in range(1,25):
    fmlp_successes.append(get_success_rate(f"p_fmlp_{i}.log"))
    pip_successes.append(get_success_rate(f"p_pip_{i}.log"))
    
    
vars = [(0,5), (5,8), (8,12), (12,17), (17,20), (20,24)]
titles = ['U_norm', 'Number of requests per resource', 'Number of resources', 'CSP', 'Number of tasks', 'Number of CPUs']
xs = [['0.1', '0.3', '0.5', '0.7', '1'],
      ['10', '30', '50'],
      ['2', '4', '6', '8'],
      ['0.1', '0.3', '0.5', '0.7', '1'],
      ['4', '6', '8'],
      ['4', '8', '16', '32']]
fig, axs = plt.subplots(3, 2, figsize=(8, 12))

for i, ax in enumerate(axs.flat):
    (start, end) = vars[i]
    ax.bar(xs[i], fmlp_successes[start:end])
    ax.set_title(titles[i])

plt.tight_layout()
plt.show()
