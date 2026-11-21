// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset", {
	refresh(frm) {
		if (frm.is_new() || !frm.fields_dict.hse_fit_for_use) return;
		if (!frm.doc.hse_fit_for_use) {
			frm.dashboard.set_headline_alert(
				__("Not fit for use: failed inspection or expired certificate. Rental dispatch is blocked."),
				"red"
			);
		} else if (frm.doc.hse_certificate_expiry) {
			const days = frappe.datetime.get_day_diff(frm.doc.hse_certificate_expiry, frappe.datetime.get_today());
			if (days <= 30) {
				frm.dashboard.set_headline_alert(
					__("Equipment certificate expires in {0} days", [days]),
					"orange"
				);
			}
		}
		frm.add_custom_button(
			__("Equipment Inspection"),
			() => frappe.new_doc("Equipment Inspection", { asset: frm.doc.name }),
			__("Create")
		);
	},
});
