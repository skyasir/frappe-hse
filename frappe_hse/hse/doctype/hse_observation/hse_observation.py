# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import today

from frappe_hse.utils import apply_risk


class HSEObservation(Document):
	def validate(self):
		apply_risk(self)
		if self.observation_type == "Positive Observation" and self.is_new():
			self.status = "Closed"
		if self.status == "Closed" and not self.closed_on:
			self.closed_on = today()
		elif self.status == "Open":
			self.closed_on = None
