# Baseline sigma level and DPMO

The sigma level expresses process performance on a common scale derived from the
defect rate, allowing very different processes to be compared.

## DPMO
Defects Per Million Opportunities normalizes the defect rate:
DPMO = (defects / (units * opportunities_per_unit)) * 1,000,000.

## Sigma level and the 1.5 sigma shift
The process sigma level is computed from the yield (1 - DPMO/1e6). By long-standing
Six Sigma convention a 1.5 sigma shift is added to account for long-term drift, so a
"six sigma" process corresponds to about 3.4 DPMO. A 3-sigma process corresponds to
roughly 66,800 DPMO.

## Relationship to capability
Capability indices and sigma level are two views of the same reality. A process with
Ppk well below 1.0 will show a high DPMO and a low sigma level. Reporting both the
capability index and the baseline sigma gives a complete, defensible baseline.
