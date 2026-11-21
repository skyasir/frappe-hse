# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

OPEN = ("Open", "In Progress")


class HSECorrectiveAction(Document):
	def validate(self):
		if not self.source:
			if self.incident:
				self.source = "Incident"
			elif self.observation:
				self.source = "Observation"
			elif self.equipment_inspection:
				self.source = "Inspection"
			elif self.risk_assessment:
				self.source = "Risk Assessment"
		if self.status in ("Completed", "Verified") and not self.completed_on:
			self.completed_on = today()
		if self.status == "Verified":
			self.verified_by = self.verified_by or frappe.session.user
			self.verified_on = self.verified_on or today()
		self.is_overdue = int(self.status in OPEN and getdate(self.due_date) < getdate(today()))

	def on_update(self):
		self.update_incident()

	def on_trash(self):
		self.update_incident(deleting=True)

	def update_incident(self, deleting=False):
		before = self.get_doc_before_save()
		incidents = {self.incident, before.incident if before else None} - {None, ""}
		for name in incidents:
			incident = frappe.get_doc("HSE Incident", name)
			if incident.docstatus == 1:
				incident.update_status(exclude_action=self.name if deleting else None)


def mark_overdue():
	"""Daily: flag open actions that are past their due date."""
	frappe.db.set_value(
		"HSE Corrective Action",
		{"status": ("in", OPEN), "due_date": ("<", today()), "is_overdue": 0},
		"is_overdue",
		1,
		update_modified=False,
	)
	frappe.db.set_value(
		"HSE Corrective Action",
		{"status": ("not in", OPEN), "is_overdue": 1},
		"is_overdue",
		0,
		update_modified=False,
	)
