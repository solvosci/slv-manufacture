1.  Go to *Inventory \> Configuration \> Operation Types*.
2.  Open the manufacturing operation type you want to use for
    classification, and check *Is Classification Operation*.
3.  Go to *Manufacturing \> Operations \> Manufacturing Orders* and
    create a new order using that operation type, with a Bill of
    Materials that has a single raw/bulk component and one or more
    finished products/byproducts.
4.  Confirm the order.
5.  Click *Classify*.
6.  For each line, enter the quantity actually obtained for that
    product. For products tracked by lot, either select an existing
    lot or type a name for a new one.
7.  If the total distributed differs from the initially planned
    quantity, check *Confirm even if it differs from the plan* to
    proceed anyway. This adjusts the demand on the underlying stock
    move to match the total distributed.
8.  Click *Confirm Classification*. If *Complete Manufacturing Order*
    is checked, the order is marked as done immediately; otherwise it
    is left ready to be completed manually.

You can classify the same order more than once before marking it
done: reopening the wizard adjusts the previous distribution instead
of starting over.
