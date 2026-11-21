# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime

from frappe_hse.utils import get_asset_fitness, get_settings, has_valid_competency

MOVING = ("Approved", "In Transit", "Arrived")


class JourneyManagementPlan(Document):
	def validate(self):
		if self.planned_arrival and get_datetime(self.planned_arrival) <= get_datetime(
			self.planned_departure
		):
			frappe.throw(_("Planned Arrival must be after Planned Departure"))
		cert_type = get_settings().driver_certificate_type
		self.driver_certificate_valid = int(
			not cert_type or has_valid_competency(self.driver, cert_type, self.planned_departure)
		)
		if self.status in MOVING:
			self.check_ready()
		if self.status == "In Transit" and not self.actual_departure:
			self.actual_departure = now_datetime()
		if self.status == "Arrived":
			self.actual_departure = self.actual_departure or self.planned_departure
			self.actual_arrival = self.actual_arrival or now_datetime()

	def check_ready(self):
		missing = []
		if not self.vehicle_inspected:
			missing.append(_("vehicle pre-trip inspection"))
		if not self.ivms_working:
			missing.append(_("IVMS check"))
		if not self.driver_rested:
			missing.append(_("driver fatigue declaration"))
		if missing:
			frappe.throw(_("Complete the pre-journey checks first: {0}").format(", ".join(missing)))
		if not self.driver_certificate_valid:
			frappe.throw(
				_("{0} has no valid {1} certificate and cannot drive this journey").format(
					self.driver_name, get_settings().driver_certificate_type
				)
			)
		if self.night_driving and not self.journey_manager:
			frappe.throw(_("Night driving needs a Journey Manager to approve it"))
		fit, reason = get_asset_fitness(self.vehicle, self.planned_departure)
		if not fit:
			frappe.throw(reason)
