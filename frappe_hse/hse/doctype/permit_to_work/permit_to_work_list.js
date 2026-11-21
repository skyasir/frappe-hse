// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.listview_settings["Permit to Work"] = {
	add_fields: ["status"],
	has_indicator_for_draft: true,
	get_indicator(doc) {
		const colors = {
			Draft: "gray",
			Requested: "orange",
			Approved: "blue",
			Active: "green",
			Suspended: "red",
			Closed: "darkgrey",
			Rejected: "red",
			Expired: "gray",
		};
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
