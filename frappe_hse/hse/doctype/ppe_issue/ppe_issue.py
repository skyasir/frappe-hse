# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe_hse.utils import get_settings


class PPEIssue(Document):
	def before_submit(self):
		if not self.acknowledged:
			frappe.throw(_("The employee must acknowledge receiving the PPE before you submit"))

	def on_submit(self):
		warehouse = get_settings().ppe_warehouse
		stock_items = [
			row for row in self.items if frappe.db.get_value("Item", row.item_code, "is_stock_item")
		]
		if not warehouse or not stock_items:
			return
		entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Issue",
				"purpose": "Material Issue",
				"company": self.company,
				"posting_date": self.issue_date,
				"set_posting_time": 1,
				"from_warehouse": warehouse,
				"remarks": _("PPE issued to {0} ({1})").format(self.employee_name, self.name),
				"items": [
					{"item_code": row.item_code, "qty": row.qty, "s_warehouse": warehouse}
					for row in stock_items
				],
			}
		)
		entry.insert()
		entry.submit()
		self.db_set("stock_entry", entry.name)

	def on_cancel(self):
		if self.stock_entry:
			entry = frappe.get_doc("Stock Entry", self.stock_entry)
			if entry.docstatus == 1:
				entry.cancel()
