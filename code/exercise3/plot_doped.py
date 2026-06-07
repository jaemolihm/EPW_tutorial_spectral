#!/usr/bin/env python3
"""Plot the spectral function along the dense K-segment defined in kpt_dense.txt
(produced by generate_k.py). Reads default EPW output filenames, so run this
in the same directory where epw3.x was executed."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import NonUniformImage

plt.rcParams.update({'font.size': 15})

PLOT_EMIN = -0.40  # eV
PLOT_EMAX =  0.40  # eV
E_SHIFT = -0.040   # eV, rigid shift applied to DFT band for shifted plot

K = np.array([1/3, 1/3, 0.0])


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

    sigma /= 1000  # meV -> eV
    return xks, energy, sigma


def parse_epw_specfun_sup(filename):
    data = np.loadtxt(filename)
    nk = int(data[-1, 0])
    nbnd = int(data[-1, 1])
    data = data.reshape(nbnd, nk, -1, 6)
    ws = data[0, 0, :, 3]
    es = data[:, :, 0, 2]
    sigma = (data[:, :, :, 4] + 1j * data[:, :, :, 5]) / 1000
    return ws, es, sigma


def parse_epw_specfun(filename):
    data = np.loadtxt(filename)
    nk = int(data[-1, 0])
    data = data.reshape(nk, -1, 3)
    ws = data[0, :, 1]
    As = data[:, :, 2] * 1000  # 1/meV -> 1/eV
    n_int = []
    with open(filename, "r") as f:
        for line in f:
            if "Integrated spectral function" in line:
                n_int += [float(line.split()[-1])]
    return ws, As, np.array(n_int)


# -------------------------------------
# Parse EPW output (epw3.x outputs)
T = 300.0
ws, es, sigma = parse_epw_specfun_sup(f"data3/specfun_sup.elself.{T:.3f}K")
ws, As, nocc = parse_epw_specfun(f"data3/specfun.elself.{T:.3f}K")
nbnd, nk, nfreq = sigma.shape
xks, _, sigma_ahc = parse_epw_selfen("epw3.out", nk, nbnd)

# alpha = projection onto K direction (recover the alpha used in generate_k.py)
alphas = xks[0, :] / K[0]

# -------------------------------------
# Interpolate spectral function onto a denser frequency grid
ws_itp = np.linspace(ws.min(), ws.max(), 10_000, True)
dw = ws_itp[1] - ws_itp[0]
As_itp = np.zeros((nk, len(ws_itp)))
for ik in range(nk):
    for ib in range(nbnd):
        sigma_itp = np.interp(ws_itp, ws, sigma[ib, ik, :])
        As_itp[ik, :] += (1 / (ws_itp - es[ib, ik] - sigma_itp)).imag / np.pi

# -------------------------------------
# Spectral-function color plot vs alpha along K direction
dx = np.diff(alphas)
dy = np.diff(ws_itp)
assert np.allclose(dx, dx[0], atol=1e-4), "alphas are not uniformly spaced"
assert np.allclose(dy, dy[0], atol=1e-4), "ws_itp is not uniformly spaced"

fig, ax = plt.subplots(figsize=(6, 4))
im = ax.imshow(As_itp.T, origin="lower", aspect="auto",
    extent=[alphas[0] - dx[0] / 2, alphas[-1] + dx[0] / 2,
            ws_itp[0] - dy[0] / 2, ws_itp[-1] + dy[0] / 2],
    cmap="Blues", norm=plt.matplotlib.colors.LogNorm(vmin=0.1, vmax=50),
    interpolation="nearest")
cbar = plt.colorbar(im, ax=ax)
cbar.set_label(r"$A_{\mathbf{k}}(\omega)$ (1/eV)")

black_label = r"$\varepsilon_{n\mathbf{k}}^{\rm DFT}$"
red_label = (r"$\varepsilon_{n\mathbf{k}}^{\rm DFT} + \mathrm{Re}\,"
             r"\Sigma_{n\mathbf{k}}(\omega = \varepsilon_{n\mathbf{k}}^{\rm DFT})$")

for ibnd in range(nbnd):
    ax.plot(alphas, es[ibnd, :], "k-", lw=1,
            label=black_label if ibnd == 0 else None)
    ax.plot(alphas, es[ibnd, :] + sigma_ahc[ibnd, :].real, "r-", lw=1,
            label=red_label if ibnd == 0 else None)

ax.axhline(0, c="grey", lw=1)
ax.set_ylabel(r"$\omega - E_\mathrm{Fermi}$ (eV)")
ax.set_xlim([alphas[0], alphas[-1]])
ax.set_ylim([PLOT_EMIN, PLOT_EMAX])
ax.legend(fontsize=9, loc="upper right")
# Find k-point along the dense segment whose band energy is closest to E_F
# (used below for the Sigma(omega) plot). Mark it and its immediate neighbors here.
abs_e = np.abs(es)
ib_star, ik_star = np.unravel_index(np.argmin(abs_e), abs_e.shape)
ik_list = [ik_star]
colors = ["k"]


ax.set_xticks([alphas[0], alphas[-1]])
ax.set_xticklabels([f"{alphas[0]:.2f}K", f"{alphas[-1]:.2f}K"])

fig.tight_layout()
fig.savefig("graphene_spectral_doped.pdf")
print("Saved figure to graphene_spectral_doped.pdf")

# -------------------------------------
# Same spectral-function plot, but with DFT band shifted by E_SHIFT and the
# red line built from Re Sigma(omega) interpolated to the shifted band energy at each k.
es_shifted = es + E_SHIFT
re_sigma_at_shifted = np.zeros_like(es_shifted)
for ib in range(nbnd):
    for ik in range(nk):
        re_sigma_at_shifted[ib, ik] = np.interp(
            es_shifted[ib, ik], ws, sigma[ib, ik, :].real
        )

fig3, ax3 = plt.subplots(figsize=(6, 4))
im3 = ax3.imshow(As_itp.T, origin="lower", aspect="auto",
    extent=[alphas[0] - dx[0] / 2, alphas[-1] + dx[0] / 2,
            ws_itp[0] - dy[0] / 2, ws_itp[-1] + dy[0] / 2],
    cmap="Blues", norm=plt.matplotlib.colors.LogNorm(vmin=0.1, vmax=50),
    interpolation="nearest")
cbar3 = plt.colorbar(im3, ax=ax3)
cbar3.set_label(r"$A_{\mathbf{k}}(\omega)$ (1/eV)")

shift_meV = E_SHIFT * 1000
black_label_shifted = (r"$\varepsilon_{n\mathbf{k}}^{\rm DFT}"
                       + f" {shift_meV:+.0f}" + r"\,\mathrm{meV}$")
red_label_shifted = (r"$\varepsilon_{n\mathbf{k}}^{\rm DFT} + \mathrm{Re}\,"
                    r"\Sigma_{n\mathbf{k}}(\omega = \varepsilon_{n\mathbf{k}}^{\rm DFT} "
                    + f"{shift_meV:+.0f}" + r"\,\mathrm{meV})$")

for ibnd in range(nbnd):
    ax3.plot(alphas, es_shifted[ibnd, :], "k-", lw=1,
             label=black_label_shifted if ibnd == 0 else None)
    ax3.plot(alphas,
             es_shifted[ibnd, :] + re_sigma_at_shifted[ibnd, :] - E_SHIFT,
             "r-", lw=1,
             label=red_label_shifted if ibnd == 0 else None)

ax3.axhline(0, c="grey", lw=1)
ax3.set_ylabel(r"$\omega - E_\mathrm{Fermi}$ (eV)")
ax3.set_xlim([alphas[0], alphas[-1]])
ax3.set_ylim([PLOT_EMIN, PLOT_EMAX])
ax3.set_xticks([alphas[0], alphas[-1]])
ax3.set_xticklabels([f"{alphas[0]:.2f}K", f"{alphas[-1]:.2f}K"])
ax3.legend(fontsize=9, loc="upper right")

fig3.tight_layout()
fig3.savefig("graphene_spectral_doped_shifted_band.pdf")
print("Saved figure to graphene_spectral_doped_shifted_band.pdf")

# -------------------------------------
# Plot Sigma(omega) at the band ib_star, for ik_star and its two neighbors.
fig2, axes2 = plt.subplots(1, 2, figsize=(10, 4), sharex=True)
for ik, c in zip(ik_list, colors):
    label = (f"k={alphas[ik]:.3f}K, "
             f"$\\varepsilon$={es[ib_star, ik]:.3f} eV")
    axes2[0].plot(ws, sigma[ib_star, ik, :].real * 1000, color=c, label=label)
    axes2[1].plot(ws, sigma[ib_star, ik, :].imag * 1000, color=c)

for ax in axes2:
    ax.set_xlabel(r"$\omega - E_\mathrm{Fermi}$ (eV)")
    ax.axhline(0, c="grey", lw=0.5)
    ax.axvline(0, c="grey", lw=0.5)
    ax.set_xlim([PLOT_EMIN, PLOT_EMAX])
axes2[0].set_ylabel(r"Re $\Sigma(E)$ (meV)")
axes2[1].set_ylabel(r"$-$Im $\Sigma(E)$ (meV)")
axes2[0].legend(fontsize=9, loc="best")

fig2.tight_layout()
fig2.savefig("graphene_selfenergy_doped.pdf", bbox_inches="tight")
print("Saved figure to graphene_selfenergy_doped.pdf")

# -------------------------------------
# Direct comparison with xARPES self-energy (Hofmann et al.).
# Same x/y scale as graphene_xarpes_selfen.png:
#   x: E - mu in [-0.25, 0.02] eV
#   y: Sigma', -Sigma'' in [-0.02, 0.27] eV
# Re Sigma is shifted by +40 meV and -Im Sigma by +110 meV so that the
# computed curves overlay the experimental traces.
XARPES_XMIN, XARPES_XMAX = -0.25, 0.02
XARPES_YMIN, XARPES_YMAX = -0.02, 0.27
RE_SHIFT = 0.040   # eV, vertical shift for Re Sigma (blue)
IM_SHIFT = 0.110   # eV, vertical shift for -Im Sigma (red)

fig4, ax4 = plt.subplots(figsize=(6, 4.5))
ax4.plot(ws, sigma[ib_star, ik_star, :].real + RE_SHIFT, "b-", lw=1.5,
         label=(r"$\mathrm{Re}\,\Sigma(E) + "
                f"{RE_SHIFT*1000:.0f}" + r"\,\mathrm{meV}$"))
ax4.plot(ws, sigma[ib_star, ik_star, :].imag + IM_SHIFT, "r-", lw=1.5,
         label=(r"$-\mathrm{Im}\,\Sigma(E) + "
                f"{IM_SHIFT*1000:.0f}" + r"\,\mathrm{meV}$"))
ax4.set_xlabel(r"$E - \mu$ (eV)")
ax4.set_ylabel(r"$\Sigma'(E),\ -\Sigma''(E)$ (eV)")
ax4.set_xlim([XARPES_XMIN, XARPES_XMAX])
ax4.set_ylim([XARPES_YMIN, XARPES_YMAX])
ax4.legend(fontsize=11, loc="upper right")

fig4.tight_layout()
fig4.savefig("graphene_selfenergy_doped_xarpes.pdf", bbox_inches="tight")
print("Saved figure to graphene_selfenergy_doped_xarpes.pdf")
#plt.show()
