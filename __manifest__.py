# -*- coding: utf-8 -*-
{
    "name": "Payment: Vietnamese Bank Base Module",
    "summary": """
        This module is the base module for generator VietQR module.(VietQR is the Vietnam's QR standard for payment)""",
    "description": """
        This module is the base module for generator VietQR module. 
        This module will provided:
        -   All the Vietnamese bank info and bankcode which announced by State Bank of Viet Nam.
        -   Add "default bank account" field to res.company model.
        -   Add VietQR for invoice view form.
    """,
    "author": "UniCube",
    "license": "LGPL-3",
    "category": "UniCube/Localization",
    "version": "17.0.0.4",
    "website": "https://unicube.vn",
    "support": "community@unicube.vn",
    "application": True,
    "installable": True,
    # any module necessary for this one to work correctly
    "depends": ["base", "l10n_vn", "account_qr_code_emv", "base_vat"],
    # always loaded
    "data": [
        "views/account_move.xml",
        "views/invoice_sale.xml",
    ],
}
