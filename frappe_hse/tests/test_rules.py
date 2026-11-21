# Copyright (c) 2026, Yasir Shaikh and contributors
# For license information, please see license.txt

from frappe import _dict
from frappe.tests import UnitTestCase
from frappe.utils import add_days, today

from frappe_hse.hse.doctype.permit_to_work.permit_to_work import gas_result
from frappe_hse.utils import certificate_status, rating, risk_level


class TestRiskMatrix(UnitTestCase):
	def test_rating_parses_select_values(self):
		self.assertEqual(rating("3 - Possible"), 3)
		self.assertEqual(rating(5), 5)
		self.assertEqual(rating(""), 0)

	def test_bands(self):
		self.assertEqual(risk_level(0), "")
		self.assertEqual(risk_level(4), "Low")
		self.assertEqual(risk_level(6), "Medium")
		self.assertEqual(risk_level(12), "High")
		self.assertEqual(risk_level(25), "Extreme")


class TestGasTest(UnitTestCase):
	def test_safe_atmosphere_passes(self):
		row = _dict(oxygen_percent=20.9, lel_percent=0, h2s_ppm=0, co_ppm=0)
		self.assertEqual(gas_result(row), "Pass")

	def test_h2s_above_limit_fails(self):
		row = _dict(oxygen_percent=20.9, lel_percent=0, h2s_ppm=12, co_ppm=0)
		self.assertEqual(gas_result(row), "Fail")

	def test_low_oxygen_fails(self):
		row = _dict(oxygen_percent=18.0, lel_percent=0, h2s_ppm=0, co_ppm=0)
		self.assertEqual(gas_result(row), "Fail")

	def test_empty_row_has_no_result(self):
		self.assertEqual(gas_result(_dict()), "")


class TestCertificateStatus(UnitTestCase):
	def test_status(self):
		self.assertEqual(certificate_status(add_days(today(), 90), 30), "Valid")
		self.assertEqual(certificate_status(add_days(today(), 10), 30), "Expiring Soon")
		self.assertEqual(certificate_status(add_days(today(), -1), 30), "Expired")
		self.assertEqual(certificate_status(None, 30), "Valid")
