# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import Command, models, _

class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def send_notification_email(self):
        if self.state != 'done':
            return

        warehouse = self.location_id.warehouse_id
        if not warehouse or not warehouse.unbuild_close_notify_users:
            self.message_post(body=_("No warehouse or users configured for notifications."))
            return

        partners = warehouse.unbuild_close_notify_users.mapped("partner_id").filtered("email")

        if not partners:
            self.message_post(body=_("No users to notify to closed unbuild in the warehouse."))
            return

        template = self.env.ref(
            "mrp_unbuild_done_message.mail_template_unbuild_done_message"
        )

        template.sudo().with_context(
            user_name=self.env.user.name
        ).send_mail(
            self.id,
            email_values={
                "recipient_ids": [Command.set(partners.ids)],
            },
            force_send=True,
        )

        self.message_post(
            body=_("Done unbuild notification email sent to: %s")
            % ", ".join(partners.mapped("email"))
        )


    def action_unbuild(self):
        res = super().action_unbuild()
        self.send_notification_email()
        return res
