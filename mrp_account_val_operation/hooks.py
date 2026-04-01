# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
import logging

_logger = logging.getLogger(__name__)

def pre_init_hook(cr):
    cr.execute("""
        UPDATE account_move_line aml
        SET val_operation = CASE
            WHEN sm.unbuild_id IS NOT NULL AND aml.val_operation = 'out_return'
                THEN 'ub_cons'
            WHEN sm.unbuild_id IS NOT NULL AND aml.val_operation = 'in_return'
                THEN 'ub_prod'
            WHEN sm.raw_material_production_id IS NOT NULL
                THEN 'mrp_cons'
            WHEN sm.production_id IS NOT NULL
                THEN 'mrp_prod'
            ELSE aml.val_operation
        END
        FROM account_move am
        JOIN stock_move sm ON am.stock_move_id = sm.id
        WHERE aml.move_id = am.id
        AND (
                sm.unbuild_id IS NOT NULL
                OR sm.production_id IS NOT NULL
                OR sm.raw_material_production_id IS NOT NULL
        );
    """)
    _logger.info("Account Move Line Manufacture Valuation Operation: UPDATE executed successfully.")
