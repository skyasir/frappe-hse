// Copyright (c) 2026, Yasir Shaikh and contributors
// For license information, please see license.txt

frappe.query_reports["Certificate Expiry Register"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "applies_to",
			label: __("For"),
			fieldtype: "Select",
			options: ["", "Person", "Equipment"],
		},
		{ fieldname: "within_days", label: __("Expiring Within (Days)"), fieldtype: "Int", default: 60 },
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "status" && data) {
			const color = data.status === "Expired" ? "red" : "orange";
			value = `<span class="indicator-pill ${color}">${value}</span>`;
		}
		return value;
	},
};
