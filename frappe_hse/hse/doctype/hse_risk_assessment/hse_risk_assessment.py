# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe_hse.utils import check_rating, risk_level


class HSERiskAssessment(Document):
	def validate(self):
		highest_initial = highest_residual = 0
		for row in self.steps:
			li = check_rating(row.initial_likelihood, _("Likelihood"), row.idx)
			si = check_rating(row.initial_severity, _("Severity"), row.idx)
			lr = check_rating(row.residual_likelihood, _("Residual likelihood"), row.idx)
			sr = check_rating(row.residual_severity, _("Residual severity"), row.idx)
			row.initial_score = li * si
			row.residual_score = lr * sr
			highest_initial = max(highest_initial, row.initial_score)
			highest_residual = max(highest_residual, row.residual_score)
		self.highest_initial_score = highest_initial
		self.highest_residual_score = highest_residual
		self.residual_risk_level = risk_level(highest_residual)

	def before_submit(self):
		missing = [str(r.idx) for r in self.steps if not r.residual_score]
		if missing:
			frappe.throw(_("Rate the residual risk on rows {0}").format(", ".join(missing)))
		if self.residual_risk_level == "Extreme":
			frappe.throw(
				_(
					"The residual risk is still Extreme. Add controls until it is High or lower before approving."
				)
			)
