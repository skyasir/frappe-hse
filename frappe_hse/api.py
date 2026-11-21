# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import Max, Min
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

	incident = frappe.qb.DocType("HSE Incident")
	query = (
		frappe.qb.from_(incident)
		.select(Max(incident.incident_date))
		.where(incident.docstatus == 1)
		.where(incident.classification.isin(["Lost Time Injury", "Fatality"]))
	)
	if company:
		query = query.where(incident.company == company)
	last = query.run()[0][0]

	if not last:
		manhours = frappe.qb.DocType("HSE Manhours")
		query = frappe.qb.from_(manhours).select(Min(manhours.period_start))
		if company:
			query = query.where(manhours.company == company)
		last = query.run()[0][0]
	return {"value": date_diff(getdate(today()), getdate(last)) if last else 0, "fieldtype": "Int"}
