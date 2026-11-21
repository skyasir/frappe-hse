// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Toolbox Talk", {
	refresh(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Mark All Signed"), () => {
				(frm.doc.attendees || []).forEach((row) => frappe.model.set_value(row.doctype, row.name, "signed", 1));
			});
		}
	},
});
