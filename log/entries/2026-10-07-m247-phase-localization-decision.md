# Phase width localization: convergence is insufficient; redirect speed work

Archive phase-blend-20261007-182533_localization-20261007-183545.tar.gz
SHA256s and sizes verified, wrapper exit 0. Both pairs pass convergence;
production_approved remains false. No further localization files are needed.

| Both-state metal region maxima | Hard / narrow | Narrow / wide |
|---|---:|---:|
| T difference, K | 0.57456 | 0.31389 |
| epsilon1 difference | 0.001685 | 0.001401 |
| U difference, m/s | 0.42319 | 0.42788 |
| raw p_rgh difference, MPa | 1.66969 | 1.92756 |

All global epsilon differences >0.99 are in interfaceOrChanged: 1498 cells
hard/narrow, 537 narrow/wide. Of these only 281 and 3 respectively also cross
alpha=0.05. The new width changes the closure even on the same side of 0.05;
it is not merely removing crossings. Max U differences remain in gasBoth,
but large pressure changes extend through metalBoth and cannot be dismissed
as gas-only extrema. Pressure values have not been gauge aligned.

Specific narrow/wide worst epsilon cell: rank44/local14729.
Narrow alpha0.05274429328, T1338.700822 K, epsilon0; wide alpha0.05315481638,
T1327.22045 K, epsilon1. Applying the implemented smoothstep and material
constants gives narrow TS/TL1348.301/1431.859 K and wide1142.523/1214.693 K.
Both phases converge to their respective modified curves, but the wide curve
labels this sub-metal-solidus temperature fully liquid. This confirms width
dependence of the numerical mixture indicator; it is not a physical metal
liquid-fraction validation. The same epsilon drives the actual PowderSim=false
Darcy term. With DC=1e6*(1-epsilon)^2/(epsilon^3+1e-12), endpoints change DC
from 1e18 to zero. This establishes strong coupling; it does not by itself
prove the cause of every pressure extremum.

Largest pressure difference in both pairs is rank0/local9295. Alpha about
0.976–0.979, T1531.8 K, epsilon0 and U around1e-9–1e-8 m/s; raw p_rgh changes
from 15.964 kPa (hard) to1.9383 MPa (narrow) to-258.266 kPa (wide).
Poorly conditioned pressure in nearly immobile cells is a hypothesis requiring
operator/pressure-reference/flux diagnostics, not a demonstrated instability.
Existing logs show 48 pressure solves per variant, max iteration62/81/85 and
final step sum-local continuity around1.85e-10/1.86e-10/2.00e-10. Small continuity
does not bound local pressure or establish physical acceptance.

Decision: do not promote either width or start 4-um/full-track production.
Keep experimental blending default-off. Do not request another width sweep.
Phase-model work must define metal solid/liquid fraction, mixed-cell latent
enthalpy and flow masks consistently before further numerical regularisation.

Immediate speed-development target is laser internals, measured54–56% of the
short probe loop after bounded thermal iteration. First add opt-in timing and
counts for initial-ray creation/cell ownership, local tracing and MPI exchange;
retain ray paths off and width zero for matched physics regression. Select an
equivalent optimization from those measurements before changing ray counts,
update frequency or physical coupling. This is the next development plan,
not an implemented laser speedup or a new user test command.
