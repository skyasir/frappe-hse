# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff, getdate, today


@frappe.whitelist()
def days_since_last_lti(filters=None):
	"""Number card: days since the last Lost Time Injury (or since the first record)."""
	frappe.has_permission("HSE Incident", "read", throw=True)
	company = None
	if isinstance(filters, str):
		filters = frappe.parse_json(filters)
	if isinstance(filters, dict):
		company = filters.get("company")
	conditions = {"docstatus": 1, "classification": ("in", ("Lost Time Injury", "Fatality"))}
	if company:
		conditions["company"] = company
	last = frappe.db.get_value("HSE Incident", conditions, "max(incident_date)")
	if not last:
		by_company = {"company": company} if company else {}
		last = frappe.db.get_value("HSE Manhours", by_company, "min(period_start)") or frappe.db.get_value(
			"HSE Incident", {"docstatus": 1, **by_company}, "min(incident_date)"
		)
	return {"value": date_diff(getdate(today()), getdate(last)) if last else 0, "fieldtype": "Int"}
