# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, cint, date_diff, getdate, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	within = cint(filters.within_days) if filters.within_days not in (None, "") else 60
	horizon = add_days(today(), within)
	rows = []
	if filters.applies_to in (None, "", "Person"):
		rows += people(filters, horizon)
	if filters.applies_to in (None, "", "Equipment") and frappe.get_meta("Asset").has_field(
		"hse_certificate_expiry"
	):
		rows += equipment(filters, horizon)
	for row in rows:
		row.days_left = date_diff(getdate(row.expiry_date), getdate(today()))
		row.status = "Expired" if row.days_left < 0 else "Expiring Soon"
	rows.sort(key=lambda r: r.days_left)
	return columns(), rows


def people(filters, horizon):
	conditions = {"expiry_date": ("<=", horizon)}
	if filters.company:
		employees = frappe.get_all("Employee", filters={"company": filters.company}, pluck="name")
		conditions["employee"] = ("in", employees or [""])
	return [
		frappe._dict(
			category="Person",
			reference_doctype="HSE Competency",
			reference_name=r.name,
			holder=r.employee_name,
			certificate=r.certificate_type,
			certificate_no=r.certificate_no,
			expiry_date=r.expiry_date,
		)
		for r in frappe.get_all(
			"HSE Competency",
			filters=conditions,
			fields=["name", "employee_name", "certificate_type", "certificate_no", "expiry_date"],
		)
	]


def equipment(filters, horizon):
	conditions = {"docstatus": 1, "hse_certificate_expiry": ("<=", horizon)}
	if filters.company:
		conditions["company"] = filters.company
	return [
		frappe._dict(
			category="Equipment",
			reference_doctype="Asset",
			reference_name=r.name,
			holder=r.asset_name,
			certificate=_("Equipment Certificate"),
			certificate_no=r.hse_certificate_no,
			expiry_date=r.hse_certificate_expiry,
		)
		for r in frappe.get_all(
			"Asset",
			filters=conditions,
			fields=["name", "asset_name", "hse_certificate_no", "hse_certificate_expiry"],
		)
	]


def columns():
	return [
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "days_left", "label": _("Days Left"), "fieldtype": "Int", "width": 90},
		{"fieldname": "expiry_date", "label": _("Expires On"), "fieldtype": "Date", "width": 110},
		{"fieldname": "category", "label": _("For"), "fieldtype": "Data", "width": 90},
		{"fieldname": "holder", "label": _("Person / Equipment"), "fieldtype": "Data", "width": 200},
		{"fieldname": "certificate", "label": _("Certificate"), "fieldtype": "Data", "width": 200},
		{"fieldname": "certificate_no", "label": _("Certificate No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "reference_doctype", "label": _("Type"), "fieldtype": "Data", "hidden": 1},
		{
			"fieldname": "reference_name",
			"label": _("Record"),
			"fieldtype": "Dynamic Link",
			"options": "reference_doctype",
			"width": 160,
		},
	]
