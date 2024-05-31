#  Copyright (c) by The Bean Family, 2023.
#
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#  These code are maintained by The Bean Family.
import json
import logging
import re
from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import remove_accents
from odoo.addons.account_qr_code_emv.const import CURRENCY_MAPPING

""" Customize the res_partner_bank model
    - Add @static_qr to store the Napas static account QR string
    - Add compute function for @acc_holder_name to get partner name when the @partner_id is change
    - Customize the name_get function to show bank account name as 'acc_number-acc_bank_name-acc_holder_name'
"""

_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    def get_currency_code(self, currency_name=False):
        return CURRENCY_MAPPING[currency_name if currency_name else "VND"]

    def get_qr_data(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        return self._get_qr_code_url(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    def get_qr_string(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        return self._get_qr_vals(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    """_This section is Override the original 'retrieve_acc_type' function_
        Logic:
            - Check if '9704' is exist in acc_number , that is an ATM card account
            - Otherwise, that is a bank account
    """

    @api.model
    def retrieve_acc_type(self, acc_number):
        try:
            return (
                "bank" if (not acc_number or "9704" not in acc_number) else "atm_card"
            )
        except Exception:
            return super(ResPartnerBank, self).retrieve_acc_type(acc_number)

    """_This section is Override the original '_get_supported_account_types' function_
       -  The original Odoo only support 'bank' type
       -  We add more custom bank type or e-wallet account type here
    """

    @api.model
    def _get_supported_account_types(self):
        rslt = super(ResPartnerBank, self)._get_supported_account_types()
        rslt.append(("atm_card", _("ATM card")))
        return rslt

    def get_qr(self, amount=0, content=""):
        result = self._get_qr_vals(
            "emv_qr", amount, self.currency_id, self.partner_id, content, content
        )
        return result

    # Override the old _get_qr_code_vals_list() function to fixed check value type error
    def _get_qr_code_vals_list(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        tag, merchant_account_info = self._get_merchant_account_info()
        currency_code = self.get_currency_code(currency.name)
        amount = isinstance(amount, (int)) and int(amount) or amount
        merchant_name = (
            self.partner_id.name
            and self._remove_accents(self.partner_id.name)[:25]
            or "NA"
        )
        merchant_city = (
            self.partner_id.city
            and self._remove_accents(self.partner_id.city)[:15]
            or "HCM"
        )
        comment = structured_communication or free_communication or ""
        comment = re.sub(
            r"/[^ A-Za-z0-9_@.\/#&+-]+/g", "", remove_accents(comment)
        ).replace("/", "")
        additional_data_field = (
            self._get_additional_data_field(comment) if self.include_reference else None
        )
        return [
            (0, "01"),  # Payload Format Indicator
            (1, "12"),  # Dynamic QR Codes
            (tag, merchant_account_info),  # Merchant Account Information
            (52, "0000"),  # Merchant Category Code
            (53, currency_code),  # Transaction Currency
            (54, int(amount) if self.country_code == "VN" else amount),
            # Force int for VN                                              # Transaction Amount
            (58, self.country_code),  # Country Code
            (59, merchant_name),  # Merchant Name
            (60, merchant_city),  # Merchant City
            (62, additional_data_field),  # Additional Data Field
        ]
