Suggests a structured name for lots, following the pattern *CCCC_YYYYMMDD_NN*:

- *CCCC*: the product's internal reference, or name if it has no internal reference.
- *YYYYMMDD*: today's date.
- *NN*: a daily sequence per product, computed from existing lots
  sharing the same prefix.

The name is suggested automatically as soon as a product is set on a
new lot. A *Suggest Name* button is also added to
already saved lots, to regenerate the suggestion on demand (for
example, after changing the product on an existing lot), and to the
lot/serial column of a receipt's operation lines, to fill in a name
there without opening the lot itself.
