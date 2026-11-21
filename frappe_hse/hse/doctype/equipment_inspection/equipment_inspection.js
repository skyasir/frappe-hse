// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Inspection", {
	setup(frm) {
		frm.set_query("template", () => ({
			filters: frm.doc.inspection_type ? { inspection_type: frm.doc.inspection_type } : {},
		}));
		frm.set_query("inspection_agency", () => ({ filters: { disabled: 0 } }));
	},
	template(frm) {
		if (!frm.doc.template) return;
		frm.call("set_readings_from_template").then(() => frm.refresh_field("readings"));
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.result === "Fail") {
			frm.add_custom_button(__("Corrective Action"), () =>
				frappe.new_doc("HSE Corrective Action", {
					source: "Inspection",
					equipment_inspection: frm.doc.name,
					company: frm.doc.company,
					priority: "High",
				}),
				__("Create")
			);
		}
	},
});
