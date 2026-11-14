"""Display-side interval helper (leader-owned).

Scoring keeps the raw Monte Carlo q05/q95 percentiles with no forced
containment of the point estimate (see docs/data_notes.md). The UI,
however, shows the interval next to the point score; a point outside
[q05, q95] reads as an error to a viewer even though it is a legitimate
uncertainty-propagation outcome. This helper widens only the DISPLAYED
interval to include the point estimate; scored values are never changed.
"""

from __future__ import annotations

import numpy as np


def expanded_interval(
    score: float, q05: float, q95: float
) -> tuple[float, float, bool]:
    """Return displayed (lo, hi, widened) with the point score inside.

    ``widened`` is True when the point estimate fell outside the raw
    percentile interval and the displayed bounds were widened to reach it.
    Non-finite inputs pass through unchanged with ``widened=False``.
    """
    lo, hi = float(q05), float(q95)
    widened = False
    if (
        np.isfinite(score)
        and np.isfinite(lo)
        and np.isfinite(hi)
    ):
        s = float(score)
        if s < lo:
            lo, widened = s, True
        elif s > hi:
            hi, widened = s, True
    return lo, hi, widened
