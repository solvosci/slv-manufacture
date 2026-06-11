When consuming raw materials in a manufacturing order,
if the user enters a quantity to consume that is greater than 0.0 for
a component that originally had a demand of 0.0, the system will not automatically mark it as 'picked'
to ensure it is processed as a real consumption instead of being canceled.

This addon mark those consumption as `picked` when calling the `_post_inventory()` function.
