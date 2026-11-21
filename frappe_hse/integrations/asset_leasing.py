# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

"""Hooks into ERPNext Asset Leasing (Rental Agreement / Rental Dispatch), when it is installed."""

import frappe
from frappe import _
from frappe.utils import cint

from frappe_hse.utils import get_asset_fitness, get_settings, has_valid_competency


def check_dispatch(doc, method=None):
	settings = get_settings()
	if not cint(settings.block_dispatch_on_invalid_certificate):
		return
	problems = []
	for row in doc.get("items") or []:
		fit, reason = get_asset_fitness(row.asset, doc.get("dispatch_datetime"))
		if not fit:
			problems.append(reason)
	if problems:
		frappe.throw(
			"<br>".join(problems) + "<br><br>" + _("Inspect or re-certify the equipment before dispatch."),
			title=_("Equipment Not Fit for Use"),
		)


def check_operator(doc, method=None):
	settings = get_settings()
	if not (
		cint(settings.block_operator_without_competency)
		and settings.operator_certificate_type
		and doc.get("hire_type") == "Wet Hire"
	):
		return
	if not doc.get("operator"):
		frappe.throw(_("A wet hire needs an operator"))
	if not has_valid_competency(doc.operator, settings.operator_certificate_type, doc.get("start_date")):
		name = frappe.db.get_value("Employee", doc.operator, "employee_name")
		frappe.throw(
			_("{0} has no valid {1} certificate on {2}").format(
				name, settings.operator_certificate_type, frappe.format(doc.start_date, "Date")
			),
			title=_("Operator Not Competent"),
		)
