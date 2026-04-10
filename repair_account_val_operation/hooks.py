# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
import logging

_logger = logging.getLogger(__name__)

def pre_init_hook(cr):
    cr.execute("""
        UPDATE account_move_line aml
        SET val_operation = CASE
            WHEN sm.repair_id IS NOT NULL AND src.usage = 'production'
                THEN 'repair_remove'
            WHEN sm.repair_id IS NOT NULL AND src.usage = 'internal'
                THEN 'repair_add'
            ELSE aml.val_operation
        END
        FROM account_move am
        JOIN stock_move sm ON am.stock_move_id = sm.id
        JOIN stock_location src ON sm.location_id = src.id
        WHERE aml.move_id = am.id
            AND sm.repair_id IS NOT NULL;
    """)
    _logger.info("Account Move Line Repair Valuation Operation: UPDATE executed successfully.")