# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, _

class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def send_notification_email(self):
        if self.state == 'done':
            warehouse = self.location_id.get_warehouse()

            if warehouse and warehouse.unbuild_close_notify_users:

                notify_users = warehouse.unbuild_close_notify_users.filtered(lambda u: u.email)
                user_emails = ", ".join(user.email for user in notify_users)

                if user_emails:
                    template = self.env.ref('mrp_unbuild_done_message.mail_template_unbuild_done_message')

                    template.sudo().with_context(
                        email_to=user_emails,
                        user_name=self.env.user.name
                    ).send_mail(self.id, force_send=True)

                    self.message_post(
                        body=_("Done unbuild notification email sent to: %s") % user_emails
                    )
                else:
                    self.message_post(body=_("No users to notify to closed unbuild in the warehouse."))
            else:
                self.message_post(body=_("No warehouse or users configured for notifications."))


    def action_unbuild(self):
        res = super().action_unbuild()
        self.send_notification_email()
        return res
