# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, get_datetime, getdate, now_datetime

from frappe_hse.utils import apply_risk, get_settings

RECORDABLE = ("Medical Treatment Case", "Restricted Work Case", "Lost Time Injury", "Fatality")


class HSEIncident(Document):
	def validate(self):
		if get_datetime(self.incident_datetime) > now_datetime():
			frappe.throw(_("The incident date and time cannot be in the future"))
		self.incident_date = getdate(self.incident_datetime)
		if self.incident_type == "Near Miss":
			self.classification = "Near Miss"
		apply_risk(self)
		self.total_days_lost = sum(cint(p.days_lost) for p in self.persons)
		if self.classification == "Lost Time Injury" and not self.total_days_lost:
			frappe.msgprint(
				_("A Lost Time Injury normally has at least one day lost. Enter the days lost per person."),
				indicator="orange",
				alert=True,
			)
		if self.classification in RECORDABLE and not self.persons:
			frappe.throw(
				_("Add the injured person under People Involved for a {0}").format(self.classification)
			)
		if self.docstatus == 0:
			self.status = "Reported"

	def on_submit(self):
		if not self.investigation_due:
			self.db_set("investigation_due", add_days(self.incident_date, 7))
		self.update_status()
		self.notify_hse_manager()

	def on_update_after_submit(self):
		self.update_status()

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	def update_status(self, exclude_action=None):
		if self.docstatus == 2:
			status = "Cancelled"
		elif not self.investigation_completed_on:
			status = "Under Investigation"
		elif frappe.db.exists(
			"HSE Corrective Action",
			{
				"incident": self.name,
				"status": ("in", ("Open", "In Progress")),
				"name": ("!=", exclude_action or ""),
			},
		):
			status = "Actions Open"
		else:
			status = "Closed"
		if status != self.status:
			self.db_set("status", status)

	def notify_hse_manager(self):
		manager = get_settings().hse_manager
		if not manager or manager == frappe.session.user:
			return
		frappe.get_doc(
			{
				"doctype": "Notification Log",
				"for_user": manager,
				"type": "Alert",
				"document_type": self.doctype,
				"document_name": self.name,
				"subject": _("{0} reported: {1} ({2})").format(
					self.incident_type, self.title, self.classification
				),
			}
		).insert(ignore_permissions=True)
