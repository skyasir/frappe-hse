// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.listview_settings["HSE Observation"] = {
	add_fields: ["observation_type", "status"],
	get_indicator(doc) {
		if (doc.observation_type === "Positive Observation") return [__("Positive"), "green", "observation_type,=,Positive Observation"];
		return doc.status === "Open" ? [__("Open"), "orange", "status,=,Open"] : [__("Closed"), "green", "status,=,Closed"];
	},
};
