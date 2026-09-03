1.  When a manufacturing order consumes a blocked component and
    produces a purifiable finished product, the resulting lot
    inherits the most restrictive release date among the blocked
    components by default. To instead treat it as freshly received
    (the full purification hours counted from now, ignoring the
    components' remaining time), check *Restart Purification Process*
    on the manufacturing order before validating it. A finished
    product that is not itself marked *Purifiable* is never blocked,
    regardless of the components' state.
