// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Permit to Work", {
	setup(frm) {
		frm.set_query("crane", () => ({ filters: { company: frm.doc.company } }));
		frm.set_query("risk_assessment", () => ({ filters: { docstatus: 1, company: frm.doc.company } }));
	},
	refresh(frm) {
		if (frm.doc.is_critical_lift) {
			frm.dashboard.set_headline_alert(
				__("Critical lift: {0}% of crane capacity. A signed lift plan is required.", [
					flt(frm.doc.utilisation_percent, 1),
				]),
				"red"
			);
		}
		const last = (frm.doc.gas_tests || []).slice(-1)[0];
		if (last && last.result === "Fail") {
			frm.dashboard.set_headline_alert(__("Latest gas test FAILED. Do not enter or start work."), "red");
		}
	},
	permit_type(frm) {
		if (["Hot Work", "Confined Space Entry"].includes(frm.doc.permit_type)) {
			frm.set_value("gas_test_required", 1);
		}
	},
	load_weight_tonnes: (frm) => frm.trigger("calc_utilisation"),
	capacity_at_radius_tonnes: (frm) => frm.trigger("calc_utilisation"),
	calc_utilisation(frm) {
		const cap = flt(frm.doc.capacity_at_radius_tonnes);
		frm.set_value("utilisation_percent", cap ? (flt(frm.doc.load_weight_tonnes) / cap) * 100 : 0);
	},
});
