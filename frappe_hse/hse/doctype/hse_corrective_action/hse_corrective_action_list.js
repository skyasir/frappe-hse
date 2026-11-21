// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.listview_settings["HSE Corrective Action"] = {
	add_fields: ["status", "is_overdue"],
	get_indicator(doc) {
		if (doc.is_overdue) return [__("Overdue"), "red", "is_overdue,=,1"];
		const colors = { Open: "orange", "In Progress": "blue", Completed: "green", Verified: "green", Cancelled: "gray" };
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
