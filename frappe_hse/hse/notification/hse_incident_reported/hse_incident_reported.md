**{{ doc.incident_type }}** ({{ doc.classification }}) was reported on {{ frappe.format_value(doc.incident_datetime, {"fieldtype": "Datetime"}) }}.

{{ doc.title }}

Location: {{ doc.location or doc.exact_location or '-' }}

Assign an investigation lead and set the investigation due date.
