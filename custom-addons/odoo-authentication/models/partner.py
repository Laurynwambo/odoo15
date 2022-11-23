from odoo import models, fields, api,_


class PartnerExtension(models.Model):
    _inherit = 'res.partner'

    password = fields.Text(string="partner password")
    access_token_ids = fields.One2many(
        string='Access Tokens',
        comodel_name='jwt_provider.access_token',
        inverse_name='partner_id',
    )

    def send_email(self):
        for res in self:
            mail_obj = self.env['mail.mail']
            subject = f"{self.name} Welcome To Expense Manager"
            email_to = res.email
            body_html = f"""
                <html>
                <body>
                <div style="margin:0px;padding: 0px;">
                    <p style="padding: 0px; font-size: 13px;">
                        Hello {res.name} !!,
                        <br/>
                        We Are happy To Have You Here.Enjoy The Best Experience In Your expense Managment
                        <br/>
                        .
                        <br/>
                       
                    </p>
                        <p> <img src="data:image/png;base64,${self.company_id.logo}" style="width: 150px;height: 80px;" /> </p>
                <br/>
                </div>
                </body>
                </html>
            """
            mail = mail_obj.sudo().create({
                'body_html': body_html,
                'subject': subject,
                'email_to': email_to
            })
            mail.send()
            return mail