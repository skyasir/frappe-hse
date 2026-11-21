# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, cint, getdate

from frappe_hse.utils import certificate_status


class HSECompetency(Document):
	def validate(self):
		if not self.expiry_date:
			months = cint(
				frappe.db.get_value("HSE Certificate Type", self.certificate_type, "validity_months")
			)
			if months:
				self.expiry_date = add_days(add_months(self.issue_date, months), -1)
		if self.expiry_date and getdate(self.expiry_date) < getdate(self.issue_date):
			frappe.throw(_("The expiry date cannot be before the issue date"))
		self.status = certificate_status(self.expiry_date)


def refresh_status():
	"""Daily: move certificates to Expiring Soon / Expired as dates pass."""
	for row in frappe.get_all(
		"HSE Competency", filters={"expiry_date": ("is", "set")}, fields=["name", "expiry_date", "status"]
	):
		status = certificate_status(row.expiry_date)
		if status != row.status:
			frappe.db.set_value("HSE Competency", row.name, "status", status, update_modified=False)
