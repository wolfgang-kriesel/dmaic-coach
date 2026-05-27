# Process capability

Process capability compares the voice of the process (its variation) to the voice
of the customer (the specification limits). It answers: can this process reliably
meet the specification?

## Cp, Cpk, Pp, Ppk
- Cp and Cpk use the short-term, within-subgroup standard deviation and require
  rational subgroups.
- Pp and Ppk use the overall (long-term) standard deviation of the full sample.
- With ungrouped individual measurements you can only compute Pp/Ppk, because there
  are no subgroups to estimate short-term variation. Report Pp/Ppk in that case and
  state the assumption explicitly.

## Formulas (two-sided specification)
- Pp = (USL - LSL) / (6 * sigma_overall)
- Ppk = min( (USL - mean) / (3 * sigma_overall), (mean - LSL) / (3 * sigma_overall) )

Ppk accounts for centering; Pp does not. A process can have a healthy Pp but a poor
Ppk if it is off-center relative to the specification.

## Interpreting the index
A widely used threshold is Ppk >= 1.33 for a "capable" process (roughly a 4-sigma
process), and Ppk >= 1.0 as a bare minimum. A Ppk well below 1.0 means a large
fraction of output falls outside specification.
