// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Journey Management Plan", {
	refresh(frm) {
		if (frm.is_new()) return;
		const next = { Planned: "Approved", Approved: "In Transit", "In Transit": "Arrived" }[frm.doc.status];
		const label = { Approved: __("Approve Journey"), "In Transit": __("Start Journey"), Arrived: __("Mark Arrived") }[next];
		if (next) {
			frm.add_custom_button(label, () => {
				frm.set_value("status", next);
				frm.save();
			}).addClass("btn-primary");
		}
		if (!frm.doc.driver_certificate_valid) {
			frm.dashboard.set_headline_alert(__("The driver has no valid driving certificate for this date."), "red");
		}
	},
});
