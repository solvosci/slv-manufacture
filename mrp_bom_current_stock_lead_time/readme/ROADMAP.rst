XLSX generation is totally overwriting original implementation in order to add
the new columns.

The best approach should be hooking `mrp_bom_current_stock` report generation
code, and override proper methods.
