# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import add_months, cint, flt, get_first_day, get_last_day, getdate

from frappe_hse.api import days_since_last_lti
from frappe_hse.utils import get_settings

RECORDABLE = ("Medical Treatment Case", "Restricted Work Case", "Lost Time Injury", "Fatality")
COUNTS = [
	("fac", "First Aid Case"),
	("mtc", "Medical Treatment Case"),
	("rwc", "Restricted Work Case"),
	("lti", "Lost Time Injury"),
	("fatality", "Fatality"),
	("near_miss", "Near Miss"),
]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	base = cint(get_settings().frequency_base) or 1000000
	months = month_starts(filters.from_date, filters.to_date)
	rows = [build_row(filters.company, start, base) for start in months]
	return columns(base), rows, None, chart(rows), summary(rows, base, filters.company)


def month_starts(from_date, to_date):
	start, end = get_first_day(getdate(from_date)), getdate(to_date)
	out = []
	while start <= end:
		out.append(start)
		start = add_months(start, 1)
	return out


def build_row(company, start, base):
	end = get_last_day(start)
	by_company = {"company": company} if company else {}
	incidents = frappe.get_all(
		"HSE Incident",
		filters={"docstatus": 1, "incident_date": ("between", (start, end)), **by_company},
		fields=["classification", "total_days_lost", "incident_type"],
	)
	mh = frappe.qb.DocType("HSE Manhours")
	query = frappe.qb.from_(mh).select(Sum(mh.total_manhours)).where(mh.period_start == start)
	if company:
		query = query.where(mh.company == company)
	manhours = flt(query.run()[0][0])
	row = frappe._dict(month=start.strftime("%b %Y"), period_start=start, manhours=manhours)
	for key, classification in COUNTS:
		row[key] = sum(1 for i in incidents if i.classification == classification)
	row.vehicle = sum(1 for i in incidents if i.incident_type == "Vehicle Incident")
	row.spills = sum(1 for i in incidents if i.incident_type == "Environmental Spill")
	row.days_lost = sum(cint(i.total_days_lost) for i in incidents)
	row.recordable = sum(1 for i in incidents if i.classification in RECORDABLE)
	row.ltifr = flt((row.lti + row.fatality) * base / manhours, 2) if manhours else 0
	row.trir = flt(row.recordable * base / manhours, 2) if manhours else 0
	row.observations = frappe.db.count(
		"HSE Observation", {"observation_date": ("between", (start, end)), **by_company}
	)
	row.toolbox_talks = frappe.db.count(
		"Toolbox Talk", {"docstatus": 1, "talk_date": ("between", (start, end)), **by_company}
	)
	return row


def columns(base):
	per = _("per {0} hrs").format(frappe.format(base, "Int"))
	cols = [
		("month", _("Month"), "Data", 90),
		("manhours", _("Man-hours"), "Float", 110),
		("near_miss", _("Near Miss"), "Int", 90),
		("fac", _("First Aid"), "Int", 85),
		("mtc", _("MTC"), "Int", 70),
		("rwc", _("RWC"), "Int", 70),
		("lti", _("LTI"), "Int", 70),
		("fatality", _("Fatality"), "Int", 80),
		("days_lost", _("Days Lost"), "Int", 85),
		("vehicle", _("Vehicle Incidents"), "Int", 110),
		("spills", _("Spills"), "Int", 70),
		("ltifr", _("LTIFR") + f" ({per})", "Float", 150),
		("trir", _("TRIR") + f" ({per})", "Float", 150),
		("observations", _("Observations"), "Int", 100),
		("toolbox_talks", _("Toolbox Talks"), "Int", 100),
	]
	return [
		{
			"fieldname": f,
			"label": label,
			"fieldtype": t,
			"width": w,
			**({"precision": 0} if f == "manhours" else {}),
		}
		for f, label, t, w in cols
	]


def chart(rows):
	return {
		"data": {
			"labels": [r.month for r in rows],
			"datasets": [
				{"name": _("Recordable"), "values": [r.recordable for r in rows], "chartType": "bar"},
				{"name": _("Near Miss"), "values": [r.near_miss for r in rows], "chartType": "bar"},
				{"name": _("TRIR"), "values": [r.trir for r in rows], "chartType": "line"},
			],
		},
		"type": "axis-mixed",
		"colors": ["#e24c4c", "#f8a33c", "#2490ef"],
	}


def summary(rows, base, company):
	manhours = sum(r.manhours for r in rows)
	lti = sum(r.lti + r.fatality for r in rows)
	recordable = sum(r.recordable for r in rows)
	return [
		{"label": _("Man-hours"), "value": manhours, "datatype": "Float", "precision": 0},
		{
			"label": _("Lost Time Injuries"),
			"value": lti,
			"datatype": "Int",
			"indicator": "Red" if lti else "Green",
		},
		{"label": _("LTIFR"), "value": flt(lti * base / manhours, 2) if manhours else 0, "datatype": "Float"},
		{
			"label": _("TRIR"),
			"value": flt(recordable * base / manhours, 2) if manhours else 0,
			"datatype": "Float",
		},
		{
			"label": _("Days Since Last LTI"),
			"value": days_since_last_lti({"company": company} if company else None)["value"],
			"datatype": "Int",
			"indicator": "Green",
		},
	]
