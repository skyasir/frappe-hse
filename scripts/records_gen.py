"""Write Frappe HSE's standard records: reports, number cards, charts, dashboard, workspace,
sidebars, dock and notifications. Run `python records_gen.py` from this folder, then migrate.
Frappe re-imports a record only when `modified` changes, so bump TS after editing."""

import json
from pathlib import Path

from doctype_gen import scrub

APP = "frappe_hse"
ROOT = Path(__file__).resolve().parents[1] / APP
TS = "2026-11-22 10:00:00.000000"
HSE = "HSE"
SETUP = "HSE Setup"
VIEW_ROLES = ["HSE Manager", "HSE Officer", "HSE User", "System Manager"]
COMPANY_FILTER = 'frappe.defaults.get_user_default(\\"Company\\")'


def write(module, folder, name, data):
	path = ROOT / scrub(module) / folder / scrub(name)
	path.mkdir(parents=True, exist_ok=True)
	(ROOT / scrub(module) / folder / "__init__.py").touch()
	(path / "__init__.py").touch()
	base = {
		"creation": TS,
		"docstatus": 0,
		"idx": 0,
		"modified": TS,
		"modified_by": "Administrator",
		"name": name,
		"owner": "Administrator",
	}
	(path / f"{scrub(name)}.json").write_text(json.dumps({**base, **data}, indent=1, sort_keys=True) + "\n")
	return path


# --------------------------------------------------------------------------- reports

REPORTS = [
	("HSE Statistics", "HSE Incident"),
	("Certificate Expiry Register", "HSE Competency"),
]
for name, ref in REPORTS:
	write(
		HSE,
		"report",
		name,
		{
			"add_total_row": 0,
			"columns": [],
			"disabled": 0,
			"doctype": "Report",
			"filters": [],
			"is_standard": "Yes",
			"module": HSE,
			"prepared_report": 0,
			"ref_doctype": ref,
			"report_name": name,
			"report_type": "Script Report",
			"roles": [{"role": r} for r in VIEW_ROLES],
		},
	)

# --------------------------------------------------------------------------- number cards


def card(name, doctype, filters, color, *, company=True, function="Count", field=None, method=None):
	data = {
		"color": color,
		"doctype": "Number Card",
		"document_type": doctype if not method else "",
		"filters_json": json.dumps(filters),
		"dynamic_filters_json": (
			json.dumps([[doctype, "company", "=", COMPANY_FILTER.replace('\\"', '"')]])
			if company and not method
			else ""
		),
		"function": function,
		"is_public": 1,
		"is_standard": 1,
		"label": name,
		"module": HSE,
		"show_full_number": 1,
		"show_percentage_stats": 0,
		"stats_time_interval": "Monthly",
		"type": "Custom" if method else "Document Type",
	}
	if field:
		data["aggregate_function_based_on"] = field
	if method:
		data["method"] = method
		data["filters_json"] = "{}"
	write(HSE, "number_card", name, data)
	return name


CARDS = [
	card("Days Since Last LTI", "", {}, "#29CD42", method="frappe_hse.api.days_since_last_lti"),
	card(
		"Open Incidents",
		"HSE Incident",
		[["HSE Incident", "status", "in", ["Reported", "Under Investigation", "Actions Open"]]],
		"#E24C4C",
	),
	card("Active Permits", "Permit to Work", [["Permit to Work", "status", "=", "Active"]], "#2490EF"),
	card(
		"Overdue Corrective Actions",
		"HSE Corrective Action",
		[["HSE Corrective Action", "is_overdue", "=", 1]],
		"#F8814F",
	),
	card(
		"Certificates Expiring",
		"HSE Competency",
		[["HSE Competency", "status", "in", ["Expiring Soon", "Expired"]]],
		"#ECAD4B",
		company=False,
	),
	card(
		"Equipment Not Fit for Use",
		"Asset",
		[["Asset", "hse_fit_for_use", "=", 0], ["Asset", "docstatus", "=", 1]],
		"#CB2929",
	),
	card(
		"Observations This Month",
		"HSE Observation",
		[["HSE Observation", "observation_date", "Timespan", "this month"]],
		"#5E64FF",
	),
]

# --------------------------------------------------------------------------- charts


def chart(name, doctype, *, kind, filters, based_on=None, group_by=None, timespan="Last Year", width="Half"):
	data = {
		"chart_name": name,
		"chart_type": "Count" if kind == "timeseries" else "Group By",
		"doctype": "Dashboard Chart",
		"document_type": doctype,
		"dynamic_filters_json": json.dumps([[doctype, "company", "=", COMPANY_FILTER.replace('\\"', '"')]]),
		"filters_json": json.dumps(filters),
		"is_public": 1,
		"is_standard": 1,
		"module": HSE,
		"number_of_groups": 0,
		"timeseries": 1 if kind == "timeseries" else 0,
		"type": "Bar" if kind == "timeseries" else kind,
		"use_report_chart": 0,
		"y_axis": [],
	}
	if kind == "timeseries":
		data.update({"based_on": based_on, "time_interval": "Monthly", "timespan": timespan})
	else:
		data.update({"group_by_type": "Count", "group_by_based_on": group_by})
	write(HSE, "dashboard_chart", name, data)
	return name, width


CHARTS = [
	chart(
		"Incidents by Month",
		"HSE Incident",
		kind="timeseries",
		based_on="incident_date",
		filters=[["HSE Incident", "docstatus", "=", 1]],
		width="Full",
	),
	chart(
		"Incidents by Classification",
		"HSE Incident",
		kind="Donut",
		group_by="classification",
		filters=[["HSE Incident", "docstatus", "=", 1]],
	),
	chart(
		"Incidents by Type",
		"HSE Incident",
		kind="Bar",
		group_by="incident_type",
		filters=[["HSE Incident", "docstatus", "=", 1]],
	),
	chart(
		"Observations by Category",
		"HSE Observation",
		kind="Bar",
		group_by="category",
		filters=[],
	),
	chart(
		"Corrective Actions by Status",
		"HSE Corrective Action",
		kind="Pie",
		group_by="status",
		filters=[],
	),
	chart(
		"Permits by Type",
		"Permit to Work",
		kind="Bar",
		group_by="permit_type",
		filters=[["Permit to Work", "docstatus", "=", 1]],
	),
]

write(
	HSE,
	"dashboard",
	"HSE",
	{
		"cards": [{"card": c} for c in CARDS],
		"charts": [{"chart": c, "width": w} for c, w in CHARTS],
		"dashboard_name": "HSE",
		"doctype": "Dashboard",
		"is_default": 0,
		"is_standard": 1,
		"module": HSE,
	},
)

# --------------------------------------------------------------------------- workspace

SHORTCUTS = [
	(
		"HSE Incident",
		"Red",
		[["HSE Incident", "status", "!=", "Closed"], ["HSE Incident", "docstatus", "=", 1]],
		"{} Open",
	),
	("Permit to Work", "Green", [["Permit to Work", "status", "=", "Active"]], "{} Active"),
	("HSE Observation", "Orange", [["HSE Observation", "status", "=", "Open"]], "{} Open"),
	("HSE Corrective Action", "Red", [["HSE Corrective Action", "is_overdue", "=", 1]], "{} Overdue"),
	("Equipment Inspection", "Blue", [], ""),
	(
		"Journey Management Plan",
		"Orange",
		[["Journey Management Plan", "status", "=", "In Transit"]],
		"{} In Transit",
	),
	("HSE Risk Assessment", "Grey", [], ""),
	("Toolbox Talk", "Grey", [], ""),
	("HSE Competency", "Yellow", [["HSE Competency", "status", "!=", "Valid"]], "{} Expiring"),
	("PPE Issue", "Grey", [], ""),
]

CARD_LINKS = {
	"Incidents and Actions": [
		("DocType", "HSE Incident"),
		("DocType", "HSE Corrective Action"),
		("DocType", "HSE Observation"),
	],
	"Safe Work": [
		("DocType", "Permit to Work"),
		("DocType", "HSE Risk Assessment"),
		("DocType", "Toolbox Talk"),
	],
	"Equipment and Journeys": [
		("DocType", "Equipment Inspection"),
		("DocType", "Journey Management Plan"),
		("DocType", "Asset"),
	],
	"People": [
		("DocType", "HSE Competency"),
		("DocType", "PPE Issue"),
		("DocType", "Employee"),
	],
	"Reports": [
		("Report", "HSE Statistics"),
		("Report", "Certificate Expiry Register"),
	],
	"Setup": [
		("DocType", "HSE Settings"),
		("DocType", "HSE Certificate Type"),
		("DocType", "HSE Inspection Template"),
		("DocType", "HSE Manhours"),
	],
}


def block(kind, key, **data):
	return {"id": f"{kind[0]}_{scrub(key)[:12]}", "type": kind, "data": data}


content = [
	block("number_card", c, number_card_name=c, col=3) for c in CARDS if c != "Observations This Month"
]
content.append(block("header", "charts", text='<span class="h4"><b>Trends</b></span>', col=12))
content += [block("chart", c, chart_name=c, col=12 if w == "Full" else 6) for c, w in CHARTS[:3]]
content.append(block("header", "quick", text='<span class="h4"><b>Quick Access</b></span>', col=12))
content += [block("shortcut", s[0], shortcut_name=s[0], col=3) for s in SHORTCUTS]
content.append(block("header", "masters", text='<span class="h4"><b>Records and Reports</b></span>', col=12))
content += [block("card", c, card_name=c, col=4) for c in CARD_LINKS]

links = []
for card_name, items in CARD_LINKS.items():
	links.append(
		{
			"hidden": 0,
			"is_query_report": 0,
			"label": card_name,
			"link_count": len(items),
			"link_type": "DocType",
			"onboard": 0,
			"type": "Card Break",
		}
	)
	for link_type, target in items:
		links.append(
			{
				"hidden": 0,
				"is_query_report": int(link_type == "Report"),
				"label": target,
				"link_count": 0,
				"link_to": target,
				"link_type": link_type,
				"onboard": 0,
				"type": "Link",
			}
		)

write(
	HSE,
	"workspace",
	"HSE",
	{
		"app": APP,
		"charts": [{"chart_name": c, "label": c} for c, _w in CHARTS[:3]],
		"content": json.dumps(content),
		"custom_blocks": [],
		"doctype": "Workspace",
		"for_user": "",
		"hide_custom": 0,
		"icon": "shield-check",
		"is_hidden": 0,
		"label": "HSE",
		"links": links,
		"module": HSE,
		"number_cards": [
			{"label": c, "number_card_name": c} for c in CARDS if c != "Observations This Month"
		],
		"parent_page": "",
		"public": 1,
		"quick_lists": [],
		"restrict_to_domain": "",
		"roles": [],
		"sequence_id": 40.0,
		"shortcuts": [
			{
				"color": color,
				"doc_view": "List",
				"format": fmt,
				"label": target,
				"link_to": target,
				"stats_filter": json.dumps(filters),
				"type": "DocType",
			}
			for target, color, filters, fmt in SHORTCUTS
		],
		"title": "HSE",
		"type": "Workspace",
	},
)

# --------------------------------------------------------------------------- sidebars and dock


def item(label, link_to=None, link_type="DocType", icon=None, *, section=False, child=False):
	row = {
		"added": 0,
		"child": int(child),
		"collapsible": 1,
		"hidden": 0,
		"indent": int(section),
		"is_default_module": 0,
		"keep_closed": int(section),
		"label": label,
		"link_type": link_type,
		"open_in_new_tab": 0,
		"show_arrow": 0,
		"type": "Section Break" if section else "Link",
	}
	if link_to:
		row["link_to"] = link_to
	if icon:
		row["icon"] = icon
	return row


def sidebar(module, name, icon, items):
	write(
		module,
		"sidebar",
		name,
		{
			"app": APP,
			"doctype": "Sidebar",
			"header_icon": icon,
			"items": items,
			"module": module,
			"standard": 1,
			"title": name,
		},
	)


sidebar(
	HSE,
	"HSE",
	"shield-check",
	[
		item("Home", "HSE", "Workspace", "house"),
		item("Dashboard", "HSE", "Dashboard", "chart-column"),
		item("Incident", "HSE Incident", icon="siren"),
		item("Corrective Action", "HSE Corrective Action", icon="list-checks"),
		item("Observation", "HSE Observation", icon="eye"),
		item("Permit to Work", "Permit to Work", icon="file-badge"),
		item("Risk Assessment", "HSE Risk Assessment", icon="triangle-alert"),
		item("Toolbox Talk", "Toolbox Talk", icon="megaphone"),
		item("Equipment Inspection", "Equipment Inspection", icon="clipboard-check"),
		item("Journey Plan", "Journey Management Plan", icon="truck"),
		item("Competency", "HSE Competency", icon="graduation-cap"),
		item("PPE Issue", "PPE Issue", icon="hard-hat"),
		item("Reports", icon="notepad-text", section=True),
		item("HSE Statistics", "HSE Statistics", "Report", child=True),
		item("Certificate Expiry Register", "Certificate Expiry Register", "Report", child=True),
	],
)

sidebar(
	SETUP,
	"HSE Setup",
	"settings",
	[
		item("HSE Settings", "HSE Settings", icon="settings"),
		item("Certificate Type", "HSE Certificate Type", icon="badge-check"),
		item("Inspection Template", "HSE Inspection Template", icon="clipboard-list"),
		item("Man-hours", "HSE Manhours", icon="clock"),
	],
)

dock_dir = ROOT / "dock" / APP
dock_dir.mkdir(parents=True, exist_ok=True)
(dock_dir / f"{APP}.json").write_text(
	json.dumps(
		{
			"app": APP,
			"creation": TS,
			"docstatus": 0,
			"doctype": "Dock",
			"idx": 0,
			"items": [
				{
					"added": 0,
					"hidden": 0,
					"icon": "house",
					"link_to": "HSE",
					"link_type": "Workspace",
					"title": "Home",
				},
				{
					"added": 0,
					"hidden": 0,
					"icon": "shield-check",
					"link_to": "HSE",
					"link_type": "Sidebar",
					"title": "HSE",
				},
				{
					"added": 0,
					"hidden": 0,
					"icon": "settings",
					"link_to": "HSE Setup",
					"link_type": "Sidebar",
					"title": "HSE Setup",
				},
			],
			"modified": TS,
			"modified_by": "Administrator",
			"name": APP,
			"owner": "Administrator",
			"standard": 1,
			"user": "",
		},
		indent=1,
		sort_keys=True,
	)
	+ "\n"
)

# --------------------------------------------------------------------------- notifications


def notification(name, doctype, message, **data):
	path = write(
		HSE,
		"notification",
		name,
		{
			"attach_print": 0,
			"channel": "System Notification",
			"doctype": "Notification",
			"document_type": doctype,
			"enabled": 1,
			"is_standard": 1,
			"message_type": "Markdown",
			"minutes_offset": 0,
			"module": HSE,
			"send_system_notification": 0,
			"send_to_all_assignees": 0,
			**data,
		},
	)
	(path / f"{scrub(name)}.md").write_text(message)
	py = path / f"{scrub(name)}.py"
	if not py.exists():
		py.write_text("def get_context(context):\n\t# do your magic here\n\tpass\n")


notification(
	"HSE Certificate Expiring",
	"HSE Competency",
	"The **{{ doc.certificate_type }}** certificate of **{{ doc.employee_name }}** expires on "
	'{{ frappe.format_value(doc.expiry_date, {"fieldtype": "Date"}) }}.\n\n'
	"Book the refresher training now, so the employee can keep working on site.\n",
	event="Days Before",
	date_changed="expiry_date",
	days_in_advance=30,
	recipients=[{"receiver_by_role": "HSE Manager"}, {"receiver_by_role": "HSE Officer"}],
	subject="Certificate expires in 30 days: {{ doc.employee_name }} - {{ doc.certificate_type }}",
)

notification(
	"HSE Incident Reported",
	"HSE Incident",
	"**{{ doc.incident_type }}** ({{ doc.classification }}) was reported on "
	'{{ frappe.format_value(doc.incident_datetime, {"fieldtype": "Datetime"}) }}.\n\n'
	"{{ doc.title }}\n\nLocation: {{ doc.location or doc.exact_location or '-' }}\n\n"
	"Assign an investigation lead and set the investigation due date.\n",
	event="Submit",
	recipients=[{"receiver_by_role": "HSE Manager"}],
	subject="Incident reported: {{ doc.title }} ({{ doc.classification }})",
)

print("HSE records written")
