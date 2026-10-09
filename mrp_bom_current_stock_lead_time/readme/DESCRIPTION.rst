Extends mrp_bom_current_stock module to add lead time to the current stock report,
based on the stock available in the source location.
It also adds the routes of the components.

Components lead time is calculated based on the lead time of the component and the lead time of the supplier.
To calculate the lead time of the BoM selected, the maximum lead time of the components is used,
and the lead time of the BoM is added to it.
