# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

import click
import frappe

from frappe_hse.setup.custom_fields import delete_custom_fields, setup_custom_fields, setup_doctype_links
from frappe_hse.setup.seed import seed_master_data
from frappe_hse.setup.workflow import setup_permit_workflow

ROLES = ("HSE Manager", "HSE Officer", "HSE User")


def before_install():
	create_roles()


def after_install():
	try:
		setup_custom_fields()
		setup_doctype_links()
		seed_master_data()
		setup_permit_workflow()
	except Exception:
		click.secho(
			"Frappe HSE installation failed. Please re-run the install or report the issue.", fg="red"
		)
		raise


def before_migrate():
	create_roles()


def after_migrate():
	setup_custom_fields()
	setup_doctype_links()
	setup_permit_workflow()


def before_uninstall():
	delete_custom_fields()


def create_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
				ignore_permissions=True
			)
