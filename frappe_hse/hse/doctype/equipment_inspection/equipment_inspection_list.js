// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.listview_settings["Equipment Inspection"] = {
	add_fields: ["result", "docstatus"],
	get_indicator(doc) {
		if (doc.docstatus === 0) return [__("Draft"), "gray", "docstatus,=,0"];
		const colors = { Pass: "green", "Pass with Observations": "orange", Fail: "red" };
		return [__(doc.result), colors[doc.result] || "gray", "result,=," + doc.result];
	},
};
