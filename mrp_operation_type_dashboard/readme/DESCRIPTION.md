Makes the *Manufacturing* app icon open directly to a kanban dashboard
of manufacturing operation types, instead of the manufacturing order
list.

Odoo already ships this kanban view for operation types, with its
usual counters and quick actions, but only exposes it under the
Inventory app, mixed in with receipts, deliveries and internal
transfers. This module reuses that same view, filtered to
manufacturing operations only, so you no longer need to open a new
manufacturing order and check its last tab just to see which operation
type it uses.

This module does not add any field or behavior of its own: it only
reuses the core view with a different domain, set as the action of the
Manufacturing app's root menu.
