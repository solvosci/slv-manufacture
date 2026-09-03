Extends `stock_lot_quarantine` to manufacturing orders: when a
purifiable finished product is produced from purifiable components,
the resulting lot's purification state is decided automatically
instead of defaulting to sellable.

By default the finished lot inherits the most restrictive release date
among its blocked components. Checking "Restart Purification Process"
on the order instead gives it a full, fresh purification period of its
own, counted from production time.
