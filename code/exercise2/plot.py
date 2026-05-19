#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import NonUniformImage

plt.rcParams.update({'font.size': 15})

def parse_epw_selfen(filename, nk, nbnd):
    xks = np.zeros((3, nk))
    energy = np.zeros((nbnd, nk))
    sigma = np.zeros((nbnd, nk), dtype=complex)

    with open(filename, 'r') as f:
        for line in f:
            if "Electron Self-Energy using Wannier function perturbation theory" in line:
                break
        print(f.readline())
        f.readline()
        f.readline()
        for ik in range(nk):
            xks[:, ik] = [float(x) for x in f.readline().split()[-3:]]
            f.readline()
            for ib in range(nbnd):
                data = f.readline().split()
                energy[ib, ik] = float(data[3])
                sigma[ib, ik] = float(data[6]) + 1j * float(data[9])
            f.readline()
            f.readline()
            f.readline()

    sigma /= 1000 # meV to eV
    return xks, energy, sigma


def parse_epw_specfun_sup(filename):
    data = np.loadtxt(filename)
    nk = int(data[-1, 0])
    nbnd = int(data[-1, 1])

    data = data.reshape(nbnd, nk, -1, 6)
    ws = data[0, 0, :, 3]
    es = data[:, :, 0, 2]
    sigma = (data[:, :, :, 4] + 1j * data[:, :, :, 5]) / 1000 # meV to eV
    return ws, es, sigma

def parse_epw_specfun(filename):
    data = np.loadtxt(filename)
    nk = int(data[-1, 0])

    data = data.reshape(nk, -1, 3)
    ws = data[0, :, 1]
    As = data[:, :, 2] * 1000  # 1/meV to 1/eV

    n_int = []
    with open(filename, "r") as f:
        for line in f:
            if "Integrated spectral function" in line:
                n_int += [float(line.split()[-1])]
    n_int = np.array(n_int)

    return ws, As, n_int

# -------------------------------------
# Parse EPW output
use_interpolation = True
T = 300.0

ws, es, sigma = parse_epw_specfun_sup(f"specfun_sup.elself.{T:.3f}K")
ws, As, nocc = parse_epw_specfun(f"specfun.elself.{T:.3f}K")
nbnd, nk, nfreq = sigma.shape

xks, _, sigma_ahc = parse_epw_selfen("epw2.out", nk, nbnd)


# -------------------------------------
# Compute spectral function on a denser frequency grid using linear interpolation of the self-energy
# A = 1 / (w - e - sigma)
ws_itp = np.linspace(ws.min(), ws.max(), 10_000, True)
dw = ws_itp[1] - ws_itp[0]
fermi_dirac = 1 / (np.exp(ws_itp / (T * 8.61732814974056E-05)) + 1)

nocc_itp = np.zeros((nk,))
As_itp = np.zeros((nk, len(ws_itp)))
for ik in range(nk):
    for ib in range(nbnd):
        sigma_itp = np.interp(ws_itp, ws, sigma[ib, ik, :])
        As_itp[ik, :] += (1 / (ws_itp - es[ib, ik] - sigma_itp)).imag / np.pi
    nocc_itp[ik] += np.sum(As_itp[ik, :] * fermi_dirac) * dw

# -------------------------------------
if use_interpolation:
    # With interpolation
    As_plot = As_itp
    ws_plot = ws_itp
    nocc_plot = nocc_itp

else:
    # Without interpolation
    As_plot = As
    ws_plot = ws
    nocc_plot = nocc


# Set x axis
dks = np.linalg.norm(xks[:, 1:] - xks[:, :-1], axis=0)
xs = np.concatenate(([0.], np.cumsum(dks)))

fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex="col",
    gridspec_kw={'height_ratios': [3, 1], "width_ratios":[1,0.02]})

axes[1, 1].set_axis_off()

# -------------------------------------
# Plot spectral function
plt.sca(axes[0, 0])
im = NonUniformImage(axes[0, 0], interpolation='nearest',
    extent=[xs[0], xs[-1], ws_plot.min(), ws_plot.max()],
    cmap="viridis", norm=plt.matplotlib.colors.LogNorm(vmin=0.01, vmax=10))
im.set_data(xs, ws_plot, As_plot.T)
axes[0, 0].add_image(im)
cbar = plt.colorbar(im, cax=axes[0, 1])
cbar.set_label("$A_{\mathbf{k}}(\omega)$ (1/eV)")

# Plot bands
for ibnd in range(nbnd):
    plt.plot(xs, es[ibnd, :], "k-", lw=1)
    plt.plot(xs, es[ibnd, :] + sigma_ahc[ibnd, :].real, "r-", lw=1)

plt.axhline(0, c="grey", lw=1)
plt.ylabel("$\omega - E_\mathrm{Fermi}$ (eV)")
plt.ylim([ws_plot.min(), ws_plot.max()])

# -------------------------------------
# Plot integrated spectral function
plt.sca(axes[1, 0])
dw = ws_plot[1] - ws_plot[0]
# plt.plot(xs, np.sum(As_plot, axis=1) * dw, label=r"$A(\omega)$")
plt.plot(xs, nocc_plot, "-", label=r"$A(\omega) f_{\rm FD}(\omega)$", lw=2)
plt.ylabel(r"$\int A(\omega) f_{\rm FD}(\omega) d\omega$")
# plt.legend()

plt.ylim([0, 6])
for i in range(6):
    plt.axhline(i, c="k", lw=0.5, ls="--")

xs_highsym = xs[np.arange(0, 351, 50)]
for x in xs_highsym:
    for ax in axes[:, 0]:
        ax.axvline(x, c="k", lw=1)
plt.xticks(xs_highsym, ["$\Gamma$", "M", "K", "$\Gamma$", "A", "L", "H", "A"])
plt.xlim([xs[0], xs[-1]])


plt.tight_layout()
fig.savefig("mgb2_spectral.pdf")

axes[0, 0].set_ylim([-1.0, 1.5])
fig.savefig("mgb2_spectral_zoom.pdf")
#plt.show()
