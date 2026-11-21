# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

"""Starter masters: common oil and gas certificates and pre-use checklists. Created once, never overwritten."""

import frappe

# name, validity months, issuing body, mandatory
CERTIFICATE_TYPES = [
	("Defensive Driving", 24, "OPAL / approved training provider", 1),
	("Heavy Vehicle Driving Licence", 120, "Royal Oman Police", 0),
	("H2S Awareness", 24, "OPAL / approved training provider", 1),
	("Basic First Aid", 24, "Red Crescent / approved provider", 0),
	("Fire Fighting", 24, "Approved training provider", 0),
	("Mobile Crane Operator", 36, "Third-party certifying body", 0),
	("Rigger and Slinger", 36, "Third-party certifying body", 0),
	("Banksman / Signaller", 36, "Third-party certifying body", 0),
	("Forklift Operator", 36, "Third-party certifying body", 0),
	("Working at Height", 24, "Approved training provider", 0),
	("Confined Space Entry", 24, "Approved training provider", 0),
	("Permit to Work Holder", 24, "Client / approved provider", 0),
	("IOSH Managing Safely", 36, "IOSH", 0),
	("NEBOSH International General Certificate", 0, "NEBOSH", 0),
]

TEMPLATES = {
	"Mobile Crane Pre-Use Check": (
		"Pre-Use Check",
		[
			("Load moment indicator (LMI) working", "Safety Devices", 1),
			("Anti two-block / overhoist cut-out working", "Safety Devices", 1),
			("Hook safety latch in place", "Lifting Gear", 1),
			("Wire rope free of kinks, broken wires and corrosion", "Lifting Gear", 1),
			("Outriggers and pads in good condition", "Structure", 1),
			("No hydraulic leaks", "Hydraulics", 0),
			("Tyres and wheel nuts", "Chassis", 0),
			("Horn, lights and reversing alarm", "Electrical", 0),
			("Fire extinguisher present and in date", "Emergency", 0),
			("Load chart in cab", "Documents", 0),
		],
	),
	"Forklift Pre-Use Check": (
		"Pre-Use Check",
		[
			("Forks free of cracks and bends", "Lifting Gear", 1),
			("Mast chains and rollers", "Lifting Gear", 1),
			("Brakes and parking brake", "Controls", 1),
			("Seat belt", "Safety Devices", 1),
			("Reversing alarm and beacon", "Electrical", 0),
			("No hydraulic or fuel leaks", "Hydraulics", 0),
			("Tyres", "Chassis", 0),
		],
	),
	"Tanker Pre-Trip Inspection": (
		"Pre-Use Check",
		[
			("Brakes and air system", "Chassis", 1),
			("Tyres incl. spare, no cuts, correct pressure", "Chassis", 1),
			("Tank valves, manhole lids and seals closed", "Tank", 1),
			("No leaks from tank or pipework", "Tank", 1),
			("IVMS unit working", "Journey", 1),
			("Lights, indicators and reflectors", "Electrical", 0),
			("Earthing / bonding cable", "Tank", 0),
			("Spill kit on board", "Emergency", 0),
			("Fire extinguishers present and in date", "Emergency", 0),
			("First aid kit", "Emergency", 0),
			("Hazard placards / UN numbers displayed", "Documents", 0),
		],
	),
	"Lifting Equipment Thorough Examination": (
		"Third-Party Certification",
		[
			("Structural members free of cracks and deformation", "Structure", 1),
			("Load test at rated capacity", "Load Test", 1),
			("Safety devices function test", "Safety Devices", 1),
			("Wire ropes and sheaves", "Lifting Gear", 1),
			("Slew ring and bolts", "Structure", 0),
			("Markings and SWL plate legible", "Documents", 0),
		],
	),
}


def seed_master_data():
	for name, months, body, mandatory in CERTIFICATE_TYPES:
		if not frappe.db.exists("HSE Certificate Type", name):
			frappe.get_doc(
				{
					"doctype": "HSE Certificate Type",
					"certificate_type": name,
					"applies_to": "Person",
					"validity_months": months,
					"issuing_body": body,
					"is_mandatory": mandatory,
				}
			).insert(ignore_permissions=True)

	for name, (inspection_type, items) in TEMPLATES.items():
		if not frappe.db.exists("HSE Inspection Template", name):
			frappe.get_doc(
				{
					"doctype": "HSE Inspection Template",
					"template_name": name,
					"inspection_type": inspection_type,
					"items": [
						{"check_item": item, "category": category, "is_critical": critical}
						for item, category, critical in items
					],
				}
			).insert(ignore_permissions=True)

	settings = frappe.get_single("HSE Settings")
	if not settings.operator_certificate_type and not settings.driver_certificate_type:
		settings.operator_certificate_type = "Mobile Crane Operator"
		settings.driver_certificate_type = "Defensive Driving"
		settings.expiry_warning_days = settings.expiry_warning_days or 30
		settings.frequency_base = settings.frequency_base or "1000000"
		settings.critical_lift_threshold = settings.critical_lift_threshold or 75
		settings.block_dispatch_on_invalid_certificate = 1
		settings.block_operator_without_competency = 1
		settings.flags.ignore_permissions = True
		settings.save()
