// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("HSE Observation", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.observation_type !== "Positive Observation") {
			frm.add_custom_button(__("Corrective Action"), () =>
				frappe.new_doc("HSE Corrective Action", {
					source: "Observation",
					observation: frm.doc.name,
					company: frm.doc.company,
				}),
				__("Create")
			);
		}
	},
});
