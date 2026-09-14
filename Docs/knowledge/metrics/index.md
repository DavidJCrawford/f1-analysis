# Pace and degradation

* [Fuel-corrected pace](fuel-corrected-pace.md) - Normalising race lap times for the fuel the car has burned, using a per-circuit mass sensitivity in seconds per kilogram, so that pace and degradation can be read without the fuel-burn trend.
* [Tyre degradation rate](tyre-degradation-rate.md) - The per-stint rate at which lap time decays with tyre age, fitted robustly on fuel-corrected laps with a two-pass residual filter, a minimum stint length and an explicit compound offset.
* [Clean-air race pace](clean-air-race-pace.md) - A driver's or team's underlying race pace estimated from green-flag, non-pit, traffic-free laps after fuel correction, with the traffic threshold declared as a tunable parameter rather than a consensus constant.

# Strategy

* [Undercut delta](undercut-delta.md) - The seconds gained or lost by pitting earlier than a rival, decomposed into the pit-loss differential, the fresh-tyre advantage and the out-lap warm-up penalty, with the overcut as its mirror.
* [Pit loss time](pit-loss-time.md) - The lap time a driver gives up to make a pit stop, decomposed into in-lap, out-lap and standstill terms, published per circuit under green, VSC and safety-car conditions with no single global figure.

# The shape of a race

* [Race trace](race-trace.md) - Cumulative race time plotted as a delta against a constant reference pace, so that strategy, tyre state and caution periods become legible as shapes rather than as columns of lap times.
* [Gap to leader](gap-to-leader.md) - Each driver's cumulative time behind whoever leads on that lap, plotted on a square-root-compressed axis so the front of the field stays readable, with lapped cars annotated rather than plotted at a false gap.
* [Overtake detection](overtake-detection.md) - Counting on-track overtakes using the published de Groote (2021) definition rather than a naive diff of the position column, with lapping and unlapping identified as the largest source of false positives.
* [Position at corner](position-at-corner.md) - Deriving the race order at any point on track — not just at the finish line — by projecting car position telemetry onto the circuit centreline and ordering drivers by total distance travelled.

# Comparing drivers and cars

* [Teammate delta](teammate-delta.md) - The symmetric percent difference between two drivers in the same car, with explicit session-selection rules, because it is the only comparison in which machinery is held constant.
* [Driver–car decomposition](driver-car-decomposition.md) - The statistical families that attempt to separate driver skill from machinery, their correctly attributed findings, the disputed constructor variance share, and the site policy of publishing such figures only with visible uncertainty.
* [Reliability and DNF rate](reliability-dnf.md) - Era-normalised finish rates and retirement-cause classification, with the hard constraint that all 2024-onward retirement causes must come from F1DB because the Ergast-schema status field is collapsed.

