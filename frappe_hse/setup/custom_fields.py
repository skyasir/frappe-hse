# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def asset_fields(insert_after):
	return [
		{"fieldname": "hse_tab", "fieldtype": "Tab Break", "label": "HSE", "insert_after": insert_after},
		{
			"fieldname": "hse_fit_for_use",
			"fieldtype": "Check",
			"label": "Fit for Use",
			"default": "1",
			"read_only": 1,
			"in_standard_filter": 1,
			"description": "Set by the latest Equipment Inspection and certificate expiry",
			"insert_after": "hse_tab",
		},
		{
			"fieldname": "hse_last_inspection",
			"fieldtype": "Link",
			"label": "Last Inspection",
			"options": "Equipment Inspection",
			"read_only": 1,
			"insert_after": "hse_fit_for_use",
		},
		{
			"fieldname": "hse_last_inspection_date",
			"fieldtype": "Date",
			"label": "Last Inspected On",
			"read_only": 1,
			"insert_after": "hse_last_inspection",
		},
		{
			"fieldname": "hse_next_inspection_due",
			"fieldtype": "Date",
			"label": "Next Inspection Due",
			"read_only": 1,
			"insert_after": "hse_last_inspection_date",
		},
		{
			"fieldname": "hse_column_break",
			"fieldtype": "Column Break",
			"insert_after": "hse_next_inspection_due",
		},
		{
			"fieldname": "hse_certificate_no",
			"fieldtype": "Data",
			"label": "Certificate No",
			"read_only": 1,
			"insert_after": "hse_column_break",
		},
		{
			"fieldname": "hse_certificate_expiry",
			"fieldtype": "Date",
			"label": "Certificate Valid Until",
			"read_only": 1,
			"insert_after": "hse_certificate_no",
		},
	]


def setup_custom_fields():
	meta = frappe.get_meta("Asset")
	if meta.has_field("hse_tab"):
		insert_after = frappe.db.get_value(
			"Custom Field", {"dt": "Asset", "fieldname": "hse_tab"}, "insert_after"
		)
	else:
		insert_after = meta.fields[-1].fieldname
	create_custom_fields({"Asset": asset_fields(insert_after)}, ignore_validate=True)


def delete_custom_fields():
	for field in asset_fields(None):
		name = frappe.db.get_value("Custom Field", {"dt": "Asset", "fieldname": field["fieldname"]})
		if name:
			frappe.delete_doc("Custom Field", name, ignore_permissions=True)
	frappe.db.delete("DocType Link", {"custom": 1, "link_doctype": ("in", LINKED_DOCTYPES)})


# Connections shown on standard forms
DOCTYPE_LINKS = [
	("Asset", "Equipment Inspection", "asset"),
	("Asset", "HSE Incident", "asset"),
	("Asset", "Journey Management Plan", "vehicle"),
	("Employee", "HSE Competency", "employee"),
	("Employee", "PPE Issue", "employee"),
	("Employee", "Journey Management Plan", "driver"),
	("Customer", "HSE Incident", "customer"),
	("Customer", "Permit to Work", "customer"),
]
LINKED_DOCTYPES = tuple({row[1] for row in DOCTYPE_LINKS})


def setup_doctype_links():
	for parent, link_doctype, fieldname in DOCTYPE_LINKS:
		if frappe.db.exists(
			"DocType Link", {"parent": parent, "link_doctype": link_doctype, "link_fieldname": fieldname}
		):
			continue
		frappe.get_doc(
			{
				"doctype": "DocType Link",
				"parent": parent,
				"parenttype": "DocType",
				"parentfield": "links",
				"link_doctype": link_doctype,
				"link_fieldname": fieldname,
				"group": "HSE",
				"custom": 1,
			}
		).insert(ignore_permissions=True)
		frappe.clear_cache(doctype=parent)
