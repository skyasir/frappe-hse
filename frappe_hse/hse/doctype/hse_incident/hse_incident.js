// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("HSE Incident", {
	setup(frm) {
		frm.set_query("asset", () => ({ filters: { company: frm.doc.company } }));
	},
	onload(frm) {
		if (frm.is_new() && !frm.doc.incident_datetime) {
			frm.set_value("incident_datetime", frappe.datetime.now_datetime());
		}
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Corrective Action"), () =>
				frappe.new_doc("HSE Corrective Action", {
					source: "Incident",
					incident: frm.doc.name,
					company: frm.doc.company,
				}),
				__("Create")
			);
			if (!frm.doc.investigation_completed_on) {
				frm.dashboard.set_headline_alert(
					__("Investigation due {0}", [frappe.datetime.str_to_user(frm.doc.investigation_due)]),
					"orange"
				);
			}
		}
	},
	incident_type(frm) {
		if (frm.doc.incident_type === "Near Miss") frm.set_value("classification", "Near Miss");
	},
});
