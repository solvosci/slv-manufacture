Adds date_scheduled fields to MRP workorders to keep track of the first scheduled start and end dates.
These new fields are updated when the workorder is being planned from the 'Plan' button,
and they are not updated again if the workorder is re-planned, but they can be updated manually if needed.

It also hides original date_planned_start and date_planned_finished fields from the tree
view to avoid confusion with the new fields.
