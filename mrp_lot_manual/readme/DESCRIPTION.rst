Ensures that production lot is filled when production is intended to be marked
as Done.

When a production is Marked as Done from Confirmed state, every consumption and
production quantities are automatically filled, and lot/serial is automatically
generated. In other cases when lot is not set yet an error is raised. This
addon prevents that lost case, so lot is always manually filled.
