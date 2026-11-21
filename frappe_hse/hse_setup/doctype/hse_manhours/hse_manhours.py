# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt, get_first_day


class HSEManhours(Document):
	def before_naming(self):
		self.period_start = get_first_day(self.period_start)

	def validate(self):
		self.period_start = get_first_day(self.period_start)
		self.total_manhours = flt(self.employee_manhours) + flt(self.contractor_manhours)
