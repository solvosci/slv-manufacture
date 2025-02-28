# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, models
from odoo.exceptions import ValidationError


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        self.ensure_one()
        if self.mo_id and self.mo_id.finished_unbuild_id:
            raise ValidationError(
                _("Unable to unbuild: %s was already unbuilt by %s")
                % (self.mo_id.name, self.mo_id.finished_unbuild_id.name)
            )
        ret = super().action_unbuild()
        self._update_mrp_from_unbuild()
        return ret

    def _update_mrp_from_unbuild(self):
        for unbuild_id in self.filtered(
            lambda x: x.mo_id and x.state == "done"
        ):
            unbuild_id.mo_id.finished_unbuild_id = unbuild_id
