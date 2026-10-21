Fixes a side effect of *MRP Production Classification*: changing
the main product's quantity can leave two move lines for the same
product and lot instead of one, because Odoo refuses to delete the
leftover placeholder line once its move is done.

A daily scheduled action finds these pairs on classification orders
marked done, adds the placeholder's quantity to the real line, and zeroes
the placeholder out instead of removing it. 
