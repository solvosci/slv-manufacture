Adds some advanced features to MRP Unbuilds:

- *Unbuild date*. This date is used when creating stock moves, then enables to create them *in the past*.
- *Shift data*. Adds some useful data about when the unbuild is done (shift dates, stop time, etc.).
- *Tags*. Adds tags support for unbuilds.
- *Back to draft*. When an unbuild is done it's possible to take it back to the ``draft`` state. Implies *removing* stock moves and move lines, and subsequent inventory update (*).

(*) Removing, as an unsafe and not recommended operation, could lead to 
unexpected consequences. This addon provides a ``stock.move`` method for safe 
removal checking.
