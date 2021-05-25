from odoo import _, api, SUPERUSER_ID
from datetime import datetime, timedelta


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        current_employees = env['mdc.workstation'].search([
            ('current_employee_id', '!=', False)])
        for reg in current_employees:
            # Modify workstation cards with the employee in this workstation
            workstation_cards = env['mdc.card'].search(
                [('card_categ_id', '=', env.ref('mdc.mdc_card_categ_L').id)
                    , ('workstation_id', '=', reg.id)])
            if workstation_cards:
                for card in workstation_cards:
                    card.write({
                        'employee_id': reg.current_employee_id.id
                    })
