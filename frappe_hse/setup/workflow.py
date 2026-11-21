# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe

WORKFLOW = "Permit to Work Approval"

# state, docstatus, style, who may edit in this state
STATES = [
	("Draft", 0, "", "HSE Officer"),
	("Requested", 0, "Warning", "HSE Manager"),
	("Approved", 1, "Primary", "HSE Manager"),
	("Active", 1, "Success", "HSE Officer"),
	("Suspended", 1, "Danger", "HSE Officer"),
	("Closed", 1, "Info", "HSE Manager"),
	("Rejected", 0, "Danger", "HSE Manager"),
	("Expired", 1, "Inverse", "HSE Manager"),
]

# from, action, to, role
TRANSITIONS = [
	("Draft", "Request Approval", "Requested", "HSE Officer"),
	("Requested", "Approve", "Approved", "HSE Manager"),
	("Requested", "Reject", "Rejected", "HSE Manager"),
	("Rejected", "Revise", "Draft", "HSE Officer"),
	("Approved", "Start Work", "Active", "HSE Officer"),
	("Active", "Suspend", "Suspended", "HSE Officer"),
	("Suspended", "Resume", "Active", "HSE Officer"),
	("Active", "Close Permit", "Closed", "HSE Officer"),
	("Suspended", "Close Permit", "Closed", "HSE Officer"),
	("Approved", "Close Permit", "Closed", "HSE Manager"),
]


def setup_permit_workflow():
	"""Create the permit approval workflow once. Later edits made on the site are kept."""
	if frappe.db.exists("Workflow", WORKFLOW):
		return
	for state, _docstatus, style, _role in STATES:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc(
				{"doctype": "Workflow State", "workflow_state_name": state, "style": style}
			).insert(ignore_permissions=True)
	for _from, action, _to, _role in TRANSITIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
				ignore_permissions=True
			)
	frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": WORKFLOW,
			"document_type": "Permit to Work",
			"workflow_state_field": "status",
			"is_active": 1,
			"send_email_alert": 0,
			"states": [
				{"state": state, "doc_status": str(docstatus), "allow_edit": role}
				for state, docstatus, _style, role in STATES
			],
			"transitions": [
				{
					"state": from_state,
					"action": action,
					"next_state": to_state,
					"allowed": role,
					"allow_self_approval": 1,
				}
				for from_state, action, to_state, role in TRANSITIONS
			],
		}
	).insert(ignore_permissions=True)
