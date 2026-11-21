# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ToolboxTalk(Document):
	def validate(self):
		seen = set()
		for row in self.attendees:
			if row.employee in seen:
				frappe.throw(
					_("Row {0}: {1} is listed twice").format(row.idx, row.employee_name or row.employee)
				)
			seen.add(row.employee)
		self.attendee_count = len(self.attendees)

	def before_submit(self):
		unsigned = [r.employee_name or r.employee for r in self.attendees if not r.signed]
		if unsigned:
			frappe.throw(_("These attendees have not signed: {0}").format(", ".join(unsigned)))
