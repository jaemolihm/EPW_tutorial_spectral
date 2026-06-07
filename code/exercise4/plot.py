#!/usr/bin/env python3
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import NonUniformImage

plt.rcParams.update({'font.size': 15})

# Optional command-line argument: directory containing specfun_sup.phon.
# Output PDF is named mgb2_phonon[_<dirname>].pdf.
if len(sys.argv) > 1:
    data_dir = sys.argv[1].rstrip("/")
    filename = os.path.join(data_dir, "specfun_sup.phon")
    suffix = os.path.basename(data_dir).removeprefix("data.")
    out_pdf = f"mgb2_phonon_{suffix}.pdf"
else:
    filename = "specfun_sup.phon"
    out_pdf = "mgb2_phonon.pdf"

# --------------------------------------
# Parse specfun_sup file
data = np.loadtxt(filename)
nq = int(data[-1, 0])
nmodes = int(data[-1, 1])

nT = np.unique(data[:, 2]).size  # number of temperatures
# [iq, iT, iw, imode, idata]
data = data.reshape(nq, nT, -1, nmodes, 9)
ws = data[0, 0, :, 0, 5] * 1e3  # eV to meV
nw = len(ws)

T_low = data[0, 0, 0, 0, 2]
w_ph = data[:, 0, 0, :, 4] * 1e3  # eV to meV
Pi_low = data[:, 0, :, :, 6] + 1j * data[:, 0, :, :, 8]
Pi_high_0 = data[:, 0, :, :, 7]
Pi = Pi_low - Pi_high_0


xks = np.loadtxt("qpt.txt", skiprows=1)[:, :3].T
dks = np.linalg.norm(xks[:, 1:] - xks[:, :-1], axis=0)
xs = np.concatenate(([0.], np.cumsum(dks)))

ws_plot = np.linspace(ws.min(), ws.max(), 1_000, True)

eta = 0.1 # meV

# --------------------------------------
# Compute self-energy
B = np.zeros((nq, len(ws_plot)))
w_ph_low = np.zeros_like(w_ph)

for iq in range(nq):
    for imode in range(nmodes):
        wq = w_ph[iq, imode]

        w2 = wq**2 + 2 * wq * Pi[iq, 0, imode]
        w_ph_low[iq, imode] = np.sqrt(abs(w2).real) * np.sign(w2.real)

        Pi_itp = np.interp(ws_plot, ws, Pi[iq, :, imode])

        for iw in range(len(ws_plot)):
            w = ws_plot[iw]
            Pi_w = Pi_itp[iw]
            B[iq, iw] += -np.imag(2 * w / ((w + 1j * eta)**2 - wq**2 - 2 * wq * Pi_w)) / np.pi

B[B < 0] = 1e-10

fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex="col",
    gridspec_kw={'height_ratios': [3, 1], "width_ratios": [1, 0.02]})
axes[1, 1].set_axis_off()

# -------------------------------------
# Plot spectral function
plt.sca(axes[0, 0])
im = NonUniformImage(axes[0, 0], interpolation='nearest',
    extent=[xs[0], xs[-1], ws_plot.min(), ws_plot.max()], cmap="Reds",
    norm=plt.matplotlib.colors.LogNorm(vmin=0.005, vmax=5))
im.set_data(xs, ws_plot, B.T)
axes[0, 0].add_image(im)
cbar = plt.colorbar(im, cax=axes[0, 1])
cbar.set_label("$B_{\mathbf{q}}(\omega)$ (1/meV)")

# Plot bands
for i in range(nmodes):
    plt.plot(xs, w_ph[:, i], "--", c="gray", lw=1,
             label="DFPT smearing 0.05 Ry" if i == 0 else None)
    plt.plot(xs, w_ph_low[:, i], "-", c="b", lw=1,
             label=f"EPW T={T_low:.0f} K" if i == 0 else None)
plt.legend(framealpha=1.0, loc="upper center", ncol=2)

plt.axhline(0, c="grey", lw=1)
plt.ylabel("$\omega$ (meV)")
plt.ylim([ws_plot.min(), ws_plot.max()])

# -------------------------------------
# Plot integrated spectral function
plt.sca(axes[1, 0])
dw = ws_plot[1] - ws_plot[0]
plt.plot(xs, np.sum(B, axis=1) * dw, "-", label=r"$B(\omega)$", lw=2)
plt.ylabel(r"$\int B_{\mathbf{q}}(\omega) d\omega$")

plt.ylim([0, 12])
plt.yticks([0, 9])
plt.axhline(9, c="k", ls="--")

xs_highsym = xs[np.arange(0, 351, 50)]
for x in xs_highsym:
    for ax in axes[:, 0]:
        ax.axvline(x, c="k", lw=1)
plt.xticks(xs_highsym, ["$\Gamma$", "M", "K", "$\Gamma$", "A", "L", "H", "A"])
plt.xlim([xs[0], xs[-1]])


plt.tight_layout()
fig.savefig(out_pdf)
print(f"Saved figure to {out_pdf}")
#plt.show()
