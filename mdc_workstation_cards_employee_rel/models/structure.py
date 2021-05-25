from odoo import api, fields, models


class Workstation(models.Model):
    _inherit = 'mdc.workstation'

    @api.multi
    def write(self, values):
        self.ensure_one()
        # Modify cards for employee changes
        new_employee = None
        card_categ_L = self.env.ref('mdc.mdc_card_categ_L').id
        if values.get('current_employee_id', False):
            new_employee = self.env['hr.employee'].browse(values['current_employee_id'])
        if self.current_employee_id.id \
                and (new_employee is None
                     or self.current_employee_id.id != new_employee.id):
            old_employee_cards = self.env['mdc.card'].search(
                [('card_categ_id', '=', card_categ_L)
                    , ('employee_id', '=', self.current_employee_id.id)])
            if old_employee_cards:
                for card in old_employee_cards:
                    card.write({
                        'workstation_id': False
                    })
        if new_employee \
                and (not self.current_employee_id.id
                     or self.current_employee_id.id != new_employee.id):
            new_employee_cards = self.env['mdc.card'].search(
                [('card_categ_id', '=', card_categ_L)
                    , ('employee_id', '=', new_employee.id)])
            if new_employee_cards:
                for card in new_employee_cards:
                    card.write({
                        'workstation_id': self.id
                    })
        return super(Workstation, self).write(values)


class Card(models.Model):
    _inherit = 'mdc.card'
    
    def _card_categ_L_preprocess(self, values):
        """
        In this addon we don´t want to force to enter the workstation
        nor should we empty the employee field
        if 'workstation_id' in values and not values.get('workstation_id'):
            raise UserError(_('You must select a workstation for this card or select another category'))
        values.pop('employee_id', None)
        """
        values.pop('lot_id', None)
        return values
