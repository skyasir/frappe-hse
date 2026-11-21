# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, now_datetime

from frappe_hse.utils import get_asset_fitness, get_settings

GAS_TEST_TYPES = ("Hot Work", "Confined Space Entry")

# Acceptable atmosphere for entry and hot work
O2_RANGE = (19.5, 23.5)
LEL_MAX = 10.0
H2S_MAX = 10.0
CO_MAX = 25.0


def gas_result(row) -> str:
	if not any(row.get(f) not in (None, "") for f in ("oxygen_percent", "lel_percent", "h2s_ppm", "co_ppm")):
		return ""
	ok = (
		O2_RANGE[0] <= flt(row.oxygen_percent) <= O2_RANGE[1]
		and flt(row.lel_percent) < LEL_MAX
		and flt(row.h2s_ppm) < H2S_MAX
		and flt(row.co_ppm) < CO_MAX
	)
	return "Pass" if ok else "Fail"


class PermittoWork(Document):
	def validate(self):
		if get_datetime(self.valid_to) <= get_datetime(self.valid_from):
			frappe.throw(_("Valid To must be after Valid From"))
		if self.permit_type in GAS_TEST_TYPES:
			self.gas_test_required = 1
		for row in self.gas_tests:
			row.result = gas_result(row)
		self.set_lift_utilisation()

	def set_lift_utilisation(self):
		if self.permit_type != "Lifting Operation" or not flt(self.capacity_at_radius_tonnes):
			self.utilisation_percent = 0
			self.is_critical_lift = 0
			return
		self.utilisation_percent = flt(self.load_weight_tonnes) / flt(self.capacity_at_radius_tonnes) * 100
		threshold = flt(get_settings().critical_lift_threshold) or 75
		self.is_critical_lift = int(self.utilisation_percent > threshold)
		if self.utilisation_percent > 100:
			frappe.throw(_("The load is heavier than the crane can lift at this radius"))

	def before_submit(self):
		if not self.issuing_authority:
			frappe.throw(_("Set the Issuing Authority who approves this permit"))
		if not self.hazards:
			frappe.throw(_("List at least one hazard and its control measure"))
		unconfirmed = [str(h.idx) for h in self.hazards if not h.confirmed]
		if unconfirmed:
			frappe.throw(_("Confirm the control measures on hazard rows {0}").format(", ".join(unconfirmed)))
		if self.gas_test_required:
			if not self.gas_tests:
				frappe.throw(_("Record a gas test before approving this permit"))
			if self.gas_tests[-1].result != "Pass":
				frappe.throw(_("The latest gas test did not pass. The area is not safe to work in."))
		if self.permit_type == "Lifting Operation" and self.crane:
			fit, reason = get_asset_fitness(self.crane, self.valid_from)
			if not fit:
				frappe.throw(reason)

	def before_update_after_submit(self):
		for row in self.gas_tests:
			row.result = gas_result(row)
		if self.status == "Active" and get_datetime(self.valid_to) < now_datetime():
			frappe.throw(_("This permit has passed its Valid To time. Raise a new permit."))
		if self.status == "Active" and self.gas_test_required and self.gas_tests:
			if self.gas_tests[-1].result == "Fail":
				frappe.throw(_("The latest gas test failed. Suspend the permit until the area is safe."))
		if self.status == "Closed" and not self.closed_on:
			self.closed_on = now_datetime()


def expire_permits():
	"""Hourly: permits past their Valid To time can no longer be worked under."""
	for name in frappe.get_all(
		"Permit to Work",
		filters={
			"docstatus": 1,
			"status": ("in", ("Approved", "Active", "Suspended")),
			"valid_to": ("<", now_datetime()),
		},
		pluck="name",
	):
		frappe.db.set_value("Permit to Work", name, "status", "Expired")
