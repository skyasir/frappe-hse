// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.listview_settings["HSE Incident"] = {
	add_fields: ["status", "classification"],
	get_indicator(doc) {
		const colors = {
			Reported: "red",
			"Under Investigation": "orange",
			"Actions Open": "yellow",
			Closed: "green",
			Cancelled: "gray",
		};
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
