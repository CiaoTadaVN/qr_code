#   Copyright (c) by The Bean Family, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The Bean Family.
import logging
import traceback

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    qr_string = fields.Char(string="VietQR string", default=False)
    qr_raw_data = fields.Char(
        string="QR data", default=False, compute="_compute_qr_string", store=True
    )

    @api.depends(
        "amount_residual", "partner_bank_id", "name", "ref", "state", "payment_state"
    )
    def _compute_qr_string(self, txn_code="I"):
        try:
            for record in self:
                if (
                    record.company_id.country_id.code == "VN"
                    and "invoice" in record.move_type
                ):
                    # if not record.qr_id:
                    pay_content = f"{str(record.name).replace('/', '')}"
                    if record.journal_id.type == "sale":
                        pay_content = f"Pay invoice {pay_content}"
                    if record.journal_id.type == "purchase":
                        pay_content = f"Pay bill {str(record.name).replace('/', '')}"
                    record.qr_code_method = "emv_qr"
                    # structured_communication = f"{record.qr_id} {record.ref if record.ref else pay_content}"  # .replace("/","")
                    structured_communication = f"{pay_content}"  # .replace("/","")

                    get_qr_data = record.partner_bank_id.get_qr_data(
                        "emv_qr",
                        int(record.amount_residual),
                        record.currency_id,
                        "",
                        pay_content,
                        structured_communication,
                    )
                    qr_str = record.partner_bank_id.get_qr_string(
                        "emv_qr",
                        int(record.amount_residual),
                        record.currency_id,
                        "",
                        pay_content,
                        structured_communication,
                    )

                    record.qr_raw_data = get_qr_data
                    record.qr_string = qr_str
        except Exception as X:
            _logger.info(f"_compute_qr_data function have error:\n {X}")
