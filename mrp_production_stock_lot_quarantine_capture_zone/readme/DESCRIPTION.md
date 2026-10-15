Extends `stock_lot_quarantine_capture_zone` to manufacturing orders:
a finished lot inherits the capture origins of its consumed
components, so a zone closure discovered after production still
blocks it.

If the finished product is missing an INTECMAR product type present
in its consumed components, it is added automatically so the block
can be evaluated, and a note is posted on the order.
