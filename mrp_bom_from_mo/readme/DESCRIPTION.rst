Adds a button on a done Manufacturing Order (MO) that allows Manufacturing
Managers to generate a new and high priorized Bill of Materials (BoM) based
on the data actually used in that MO:

* Product (template): taken from the MO.
* Quantity: normalized to 1 unit of the product UoM.
* Components: the components actually consumed in the MO, with quantities
  proportionally recalculated for the normalized quantity.
* Operations: the operations performed in the MO.
* BoM Type: "Manufacture this product".

Before creating the BoM, the user is asked to confirm:

* The BoM reference (required).

At debug mode, it's possible to enable logging both action for the
Manufacturing Order and for the newly created Bill of Materials,
cross-referencing each other.
