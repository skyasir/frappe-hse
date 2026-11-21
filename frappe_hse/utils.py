# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, date_diff, getdate, today


def get_settings():
	return frappe.get_cached_doc("HSE Settings")


def rating(value) -> int:
	"""'3 - Possible' -> 3, 4 -> 4, '' -> 0."""
	if value in (None, ""):
		return 0
	return cint(str(value).split(" ", 1)[0])


def risk_level(score: int) -> str:
	"""5x5 matrix banding: 1-4 Low, 5-9 Medium, 10-16 High, 20-25 Extreme."""
	if not score:
		return ""
	if score <= 4:
		return "Low"
	if score <= 9:
		return "Medium"
	if score <= 16:
		return "High"
	return "Extreme"


def apply_risk(doc, prefix=""):
	p = f"{prefix}_" if prefix else ""
	score = rating(doc.get(f"{p}likelihood")) * rating(doc.get(f"{p}severity_rating"))
	doc.set(f"{p}risk_score", score)
	doc.set(f"{p}risk_level", risk_level(score))


def check_rating(value, label, row_idx=None):
	value = cint(value)
	if value and not 1 <= value <= 5:
		where = _("Row {0}: ").format(row_idx) if row_idx else ""
		frappe.throw(where + _("{0} must be between 1 and 5").format(label))
	return value


def certificate_status(expiry_date, warn_days=None) -> str:
	if not expiry_date:
		return "Valid"
	if warn_days is None:
		warn_days = cint(get_settings().expiry_warning_days) or 30
	days_left = date_diff(getdate(expiry_date), getdate(today()))
	if days_left < 0:
		return "Expired"
	if days_left <= warn_days:
		return "Expiring Soon"
	return "Valid"


def has_valid_competency(employee, certificate_type, on_date=None) -> bool:
	if not (employee and certificate_type):
		return False
	on_date = getdate(on_date or today())
	rows = frappe.get_all(
		"HSE Competency",
		filters={"employee": employee, "certificate_type": certificate_type},
		fields=["issue_date", "expiry_date"],
	)
	return any(
		getdate(r.issue_date) <= on_date and (not r.expiry_date or getdate(r.expiry_date) >= on_date)
		for r in rows
	)


def get_asset_fitness(asset, on_date=None):
	"""Return (fit, reason) for an Asset, from the HSE fields kept by Equipment Inspection."""
	meta = frappe.get_meta("Asset")
	if not meta.has_field("hse_fit_for_use"):
		return True, ""
	values = frappe.db.get_value(
		"Asset", asset, ["hse_fit_for_use", "hse_certificate_expiry", "asset_name"], as_dict=True
	)
	if not values:
		return True, ""
	on_date = getdate(on_date or today())
	if not cint(values.hse_fit_for_use):
		return False, _("{0} failed its last inspection and is not fit for use").format(values.asset_name)
	if values.hse_certificate_expiry and getdate(values.hse_certificate_expiry) < on_date:
		return False, _("The certificate of {0} expired on {1}").format(
			values.asset_name, frappe.format(values.hse_certificate_expiry, "Date")
		)
	return True, ""
