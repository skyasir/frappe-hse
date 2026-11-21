app_name = "frappe_hse"
app_title = "HSE"
app_publisher = "Yasir Shaikh"
app_description = (
	"Health, Safety and Environment (HSE) management for ERPNext: incidents, permits to work, "
	"risk assessments, inspections, competencies and journey management"
)
app_email = "erp.yasirshaikh@gmail.com"
app_license = "gpl-3.0"
required_apps = ["frappe/erpnext"]
app_home = "/desk/hse"

add_to_apps_screen = [
	{
		"name": app_name,
		"logo": "/assets/frappe_hse/images/hse.svg",
		"title": app_title,
		"route": app_home,
	}
]

before_install = "frappe_hse.install.before_install"
after_install = "frappe_hse.install.after_install"
before_migrate = "frappe_hse.install.before_migrate"
after_migrate = "frappe_hse.install.after_migrate"
before_uninstall = "frappe_hse.install.before_uninstall"

doctype_js = {
	"Asset": "public/js/asset.js",
}

# ERPNext Asset Leasing: equipment fitness and operator competency gates.
# These only fire when that app is installed.
doc_events = {
	"Rental Dispatch": {
		"before_submit": "frappe_hse.integrations.asset_leasing.check_dispatch",
	},
	"Rental Agreement": {
		"before_submit": "frappe_hse.integrations.asset_leasing.check_operator",
	},
}

scheduler_events = {
	"daily": [
		"frappe_hse.hse.doctype.hse_competency.hse_competency.refresh_status",
		"frappe_hse.hse.doctype.hse_corrective_action.hse_corrective_action.mark_overdue",
		"frappe_hse.hse.doctype.equipment_inspection.equipment_inspection.refresh_all_assets",
	],
	"hourly": [
		"frappe_hse.hse.doctype.permit_to_work.permit_to_work.expire_permits",
	],
}
