For products based on standard price cost method, it will be calculated
depending how is produced, based on BoM components and their costs.

This method will update standand price for products only if it's the
only variant and that product has a unique BoM; otherwise the price won't be
updated.

If a product BoM has components that are in the same situation (are produced,
have a single BoM and variant, and uses standard cost method), the calculation
will take in account it.
