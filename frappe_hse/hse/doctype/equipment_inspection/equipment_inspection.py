# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

CERTIFYING = ("Third-Party Certification", "Load Test")


class EquipmentInspection(Document):
	def validate(self):
		if self.template and not self.readings:
			self.set_readings_from_template()
		critical_fail = any(r.result == "Fail" and r.is_critical for r in self.readings)
		any_fail = any(r.result == "Fail" for r in self.readings)
		if critical_fail:
			self.result = "Fail"
		elif not self.result and self.readings and all(r.result for r in self.readings):
			self.result = "Pass with Observations" if any_fail else "Pass"
		if self.certificate_expiry and getdate(self.certificate_expiry) < getdate(self.inspection_date):
			frappe.throw(_("Certificate Valid Until cannot be before the inspection date"))

	@frappe.whitelist()
	def set_readings_from_template(self):
		self.set("readings", [])
		for item in frappe.get_doc("HSE Inspection Template", self.template).items:
			self.append(
				"readings",
				{"check_item": item.check_item, "category": item.category, "is_critical": item.is_critical},
			)

	def before_submit(self):
		if not self.result:
			frappe.throw(_("Set the inspection result"))
		pending = [str(r.idx) for r in self.readings if not r.result]
		if pending:
			frappe.throw(_("Record a result on checklist rows {0}").format(", ".join(pending)))
		if self.inspection_type in CERTIFYING and self.result != "Fail" and not self.certificate_expiry:
			frappe.throw(_("Enter the date the certificate is valid until"))

	def on_submit(self):
		refresh_asset_fitness(self.asset)

	def on_cancel(self):
		refresh_asset_fitness(self.asset)


def refresh_asset_fitness(asset):
	"""Copy the latest inspection result and certificate onto the Asset."""
	if not frappe.get_meta("Asset").has_field("hse_fit_for_use"):
		return
	latest = frappe.get_all(
		"Equipment Inspection",
		filters={"asset": asset, "docstatus": 1},
		fields=["name", "inspection_date", "result", "next_inspection_due"],
		order_by="inspection_date desc, creation desc",
		limit=1,
	)
	cert = frappe.get_all(
		"Equipment Inspection",
		filters={
			"asset": asset,
			"docstatus": 1,
			"inspection_type": ("in", CERTIFYING),
			"certificate_expiry": ("is", "set"),
		},
		fields=["certificate_no", "certificate_expiry"],
		order_by="inspection_date desc, creation desc",
		limit=1,
	)
	values = {
		"hse_last_inspection": latest[0].name if latest else None,
		"hse_last_inspection_date": latest[0].inspection_date if latest else None,
		"hse_next_inspection_due": latest[0].next_inspection_due if latest else None,
		"hse_certificate_no": cert[0].certificate_no if cert else None,
		"hse_certificate_expiry": cert[0].certificate_expiry if cert else None,
	}
	failed = bool(latest and latest[0].result == "Fail")
	expired = bool(cert and getdate(cert[0].certificate_expiry) < getdate(today()))
	values["hse_fit_for_use"] = int(not failed and not expired)
	frappe.db.set_value("Asset", asset, values, update_modified=False)


def refresh_all_assets():
	"""Daily: equipment whose certificate expired yesterday is no longer fit for use."""
	if not frappe.get_meta("Asset").has_field("hse_fit_for_use"):
		return
	for asset in frappe.get_all(
		"Asset",
		filters={"hse_fit_for_use": 1, "hse_certificate_expiry": ("<", today())},
		pluck="name",
	):
		frappe.db.set_value("Asset", asset, "hse_fit_for_use", 0, update_modified=False)
