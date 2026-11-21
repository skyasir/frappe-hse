// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.listview_settings["Journey Management Plan"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const colors = { Planned: "gray", Approved: "blue", "In Transit": "orange", Arrived: "green", Cancelled: "red" };
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
