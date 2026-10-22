Adds a wizard to manufacturing orders whose operation type
is marked as *Classification*. It distributes the quantity of a single
bulk/raw component across a main product and any number of byproducts
once the actual output is known, instead of relying on the quantities
originally planned in the Bill of Materials.

It is meant for processes where a bulk input is split into several
outputs of different grades or sizes, and the exact breakdown is only
known after production, not in advance.

Using *Unbuild* to reverse and re-split a manufacturing order is not a
substitute for this: Odoo blocks unbuild operations on products with
lot/serial tracking unless the unbuild is explicitly linked to the
manufacturing order that produced them.

The wizard also lets you classify the same order more than once. This
requires working around a core limitation: once a reserved quantity on
a move has been marked as picked, Odoo's own reservation logic ignores
that line entirely, in both directions - it will not pick up
additional stock to cover a higher demand, nor release part of an
excessive reservation to match a lower one, even when the change is
otherwise legitimate. The wizard adjusts the reservation explicitly
instead of relying on that mechanism.
