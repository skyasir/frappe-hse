"""DocType specs for Frappe HSE. Run `python specs_hse.py` from this folder."""

from doctype_gen import doctype

HSE = "HSE"
SETUP = "HSE Setup"

MANAGER = ("HSE Manager", "full")
OFFICER = ("HSE Officer", "write")
USER = ("HSE User", "read")
SYSMGR = ("System Manager", "full")
EMPLOYEE_REPORTER = ("Employee", "create")

STD = [SYSMGR, MANAGER, OFFICER, USER]
REPORTABLE = [SYSMGR, MANAGER, OFFICER, ("HSE User", "create"), EMPLOYEE_REPORTER]
SETUP_ROLES = [SYSMGR, MANAGER, ("HSE Officer", "read"), USER]

RISK_LEVELS = "\\nLow\\nMedium\\nHigh\\nExtreme"
LIKELIHOOD = "\\n1 - Rare\\n2 - Unlikely\\n3 - Possible\\n4 - Likely\\n5 - Almost Certain"
SEVERITY = "\\n1 - Insignificant\\n2 - Minor\\n3 - Moderate\\n4 - Major\\n5 - Catastrophic"
OBS_CATEGORIES = (
	"\\nPPE\\nHousekeeping\\nDriving & Journey\\nLifting & Rigging\\nWorking at Height"
	"\\nElectrical\\nFire & Hot Work\\nConfined Space\\nH2S & Gas\\nEnvironment & Waste"
	"\\nTools & Equipment\\nManual Handling\\nProcedures\\nOther"
)


def risk_block(prefix="", label="Risk"):
	p = f"{prefix}_" if prefix else ""
	return [
		f"{p}likelihood:Select:Likelihood|opt={LIKELIHOOD}",
		f"{p}severity_rating:Select:Severity|opt={SEVERITY}",
		f"{p}risk_score:Int:{label} Score|ro",
		f"{p}risk_level:Select:{label} Level|opt={RISK_LEVELS}|ro",
	]


# --------------------------------------------------------------------------- setup


doctype(
	"HSE Settings",
	SETUP,
	[
		"general_section:Section Break:General",
		"hse_manager:Link:HSE Manager|opt=User|desc=Gets incident and overdue-action alerts",
		"expiry_warning_days:Int:Warn Before Expiry (Days)|default=30",
		"column_break_gen:Column Break",
		"frequency_base:Select:Frequency Rate Base|opt=1000000\\n200000|default=1000000"
		"|desc=LTIFR and TRIR are per this many man-hours (1,000,000 for OPAL/PDO, 200,000 for OSHA)",
		"critical_lift_threshold:Percent:Critical Lift Above (% of Crane Capacity)|default=75",
		"equipment_section:Section Break:Equipment and Operators",
		"block_dispatch_on_invalid_certificate:Check:Block Rental Dispatch Without a Valid Equipment Certificate|default=1"
		"|desc=Needs ERPNext Asset Leasing. Stops dispatch of equipment that is not fit for use or whose certificate has expired.",
		"block_operator_without_competency:Check:Block Wet Hire Without a Competent Operator|default=1",
		"column_break_eq:Column Break",
		"operator_certificate_type:Link:Operator Certificate|opt=HSE Certificate Type",
		"driver_certificate_type:Link:Driver Certificate|opt=HSE Certificate Type"
		"|desc=Checked on journey plans, e.g. OPAL defensive driving",
		"ppe_section:Section Break:PPE",
		"ppe_warehouse:Link:PPE Store Warehouse|opt=Warehouse"
		"|desc=When set, submitting a PPE Issue posts a Material Issue from this warehouse",
	],
	issingle=True,
	roles=[SYSMGR, MANAGER, ("HSE Officer", "read")],
)

doctype(
	"HSE Certificate Type",
	SETUP,
	[
		"certificate_type:Data:Certificate Type|reqd|unique|bold",
		"applies_to:Select:Applies To|opt=Person\\nEquipment|default=Person|reqd|list|filter",
		"validity_months:Int:Validity (Months)|list|desc=Fills the expiry date from the issue date",
		"column_break_1:Column Break",
		"issuing_body:Data:Typical Issuing Body",
		"is_mandatory:Check:Mandatory for Field Staff|list",
		"description:Small Text:Description",
	],
	autoname="field:certificate_type",
	naming_rule="By fieldname",
	roles=SETUP_ROLES,
	quick_entry=True,
	search_fields="applies_to",
)

doctype(
	"HSE Inspection Template Item",
	SETUP,
	[
		"check_item:Data:Check Item|reqd|list|width=6",
		"category:Data:Category|list|width=3",
		"is_critical:Check:Critical|list|width=1|desc=A Fail on a critical item fails the inspection",
	],
	istable=True,
)

doctype(
	"HSE Inspection Template",
	SETUP,
	[
		"template_name:Data:Template Name|reqd|unique|bold",
		"inspection_type:Select:Inspection Type|opt=\\nPre-Use Check\\nPeriodic Inspection\\nThird-Party Certification\\nLoad Test|list",
		"column_break_1:Column Break",
		"asset_category:Link:Asset Category|opt=Asset Category|list",
		"items_section:Section Break:Checklist",
		"items:Table:Checklist|opt=HSE Inspection Template Item|reqd",
	],
	autoname="field:template_name",
	naming_rule="By fieldname",
	roles=SETUP_ROLES,
)

doctype(
	"HSE Manhours",
	SETUP,
	[
		"company:Link:Company|opt=Company|reqd|list|filter",
		"period_start:Date:Month Starting|reqd|list|desc=First day of the month",
		"column_break_1:Column Break",
		"employee_headcount:Int:Employee Headcount",
		"contractor_headcount:Int:Contractor Headcount",
		"hours_section:Section Break:Man-hours",
		"employee_manhours:Float:Employee Man-hours|precision=0",
		"contractor_manhours:Float:Contractor Man-hours|precision=0",
		"column_break_2:Column Break",
		"total_manhours:Float:Total Man-hours|ro|list|bold|precision=0",
		"km_driven:Float:Kilometres Driven|precision=0|desc=For the motor vehicle incident rate",
	],
	autoname="format:MH-{company}-{period_start}",
	naming_rule="Expression",
	roles=STD,
	sort_field="period_start",
)

# --------------------------------------------------------------------------- incidents

doctype(
	"HSE Incident Person",
	HSE,
	[
		"person_type:Select:Person|opt=Employee\\nContractor\\nThird Party|default=Employee|list|width=2",
		"employee:Link:Employee|opt=Employee|list|width=2",
		"person_name:Data:Name|list|width=2|fetch=employee.employee_name|if_empty=1",
		"injury_type:Select:Injury|opt=\\nNone\\nCut / Laceration\\nBruise / Contusion\\nFracture\\nSprain / Strain"
		"\\nBurn\\nEye Injury\\nInhalation / Gas Exposure\\nHeat Stress\\nCrush\\nOther|list|width=2",
		"body_part:Data:Body Part",
		"treatment:Select:Treatment|opt=\\nNone\\nFirst Aid\\nMedical Treatment\\nHospitalised|list|width=1",
		"days_lost:Int:Days Lost|list|width=1",
	],
	istable=True,
)

doctype(
	"HSE Incident",
	HSE,
	[
		"naming_series:Select:Series|opt=HSE-INC-.YYYY.-.####|reqd|default=HSE-INC-.YYYY.-.####|phide",
		"title:Data:Title|reqd|bold",
		"incident_type:Select:Incident Type|opt=\\nInjury\\nNear Miss\\nVehicle Incident\\nProperty Damage"
		"\\nEnvironmental Spill\\nFire\\nGas Release\\nDangerous Occurrence\\nSecurity|reqd|list|filter",
		"classification:Select:Classification|opt=\\nNear Miss\\nNon-Injury\\nFirst Aid Case\\nMedical Treatment Case"
		"\\nRestricted Work Case\\nLost Time Injury\\nFatality|reqd|list|filter",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd|filter",
		"incident_datetime:Datetime:Date and Time|reqd|list",
		"incident_date:Date:Incident Date|ro|hidden",
		"status:Select:Status|opt=Reported\\nUnder Investigation\\nActions Open\\nClosed\\nCancelled"
		"|default=Reported|ro|list|filter|nocopy",
		"column_break_2:Column Break",
		"reported_by:Link:Reported By|opt=Employee",
		"reported_by_name:Data:Reported By Name|fetch=reported_by.employee_name|ro",
		"is_reportable:Check:Reportable to Client|aos",
		"client_notified_on:Datetime:Client Notified On|depends=is_reportable|aos",
		"where_section:Section Break:Where",
		"location:Link:Location|opt=Location|filter",
		"exact_location:Data:Exact Spot",
		"customer:Link:Client / Site Owner|opt=Customer|filter",
		"column_break_3:Column Break",
		"project:Link:Project|opt=Project",
		"asset:Link:Equipment Involved|opt=Asset",
		"asset_name:Data:Equipment Name|fetch=asset.asset_name|ro",
		"vehicle_no:Data:Vehicle No",
		"what_section:Section Break:What Happened",
		"description:Text Editor:Description|reqd",
		"immediate_action:Small Text:Immediate Action Taken",
		"potential_section:Section Break:Potential Severity|collapsible",
	]
	+ risk_block("", "Potential Risk")
	+ [
		"people_section:Section Break:People Involved",
		"persons:Table:People|opt=HSE Incident Person",
		"total_days_lost:Int:Total Days Lost|ro",
		"loss_section:Section Break:Losses|collapsible",
		"property_damage_cost:Currency:Property Damage Cost",
		"spill_volume_litres:Float:Spill Volume (Litres)|depends=eval:doc.incident_type=='Environmental Spill'",
		"column_break_loss:Column Break",
		"spill_substance:Data:Substance Spilled|depends=eval:doc.incident_type=='Environmental Spill'",
		"investigation_tab:Tab Break:Investigation",
		"investigation_lead:Link:Investigation Lead|opt=Employee|aos",
		"investigation_lead_name:Data:Lead Name|fetch=investigation_lead.employee_name|ro",
		"investigation_due:Date:Investigation Due|aos",
		"column_break_inv:Column Break",
		"investigation_completed_on:Date:Investigation Completed On|aos|nocopy",
		"root_cause_category:Select:Root Cause Category|opt=\\nHuman Factors\\nInadequate Procedure\\nInadequate Training"
		"\\nEquipment Failure\\nInadequate Supervision\\nWork Environment\\nCommunication\\nRisk Not Assessed\\nOther|aos",
		"findings_section:Section Break",
		"why_analysis:Small Text:5-Why Analysis|aos",
		"root_cause:Small Text:Root Cause|aos",
		"lessons_learned:Small Text:Lessons Learned|aos",
		"amended_from:Link:Amended From|opt=HSE Incident|ro|nocopy|phide",
	],
	autoname="naming_series:",
	is_submittable=True,
	title_field="title",
	search_fields="incident_type,classification,status",
	roles=[SYSMGR, MANAGER, OFFICER, ("HSE User", "create"), EMPLOYEE_REPORTER],
	sort_field="incident_datetime",
	links=[
		{"link_doctype": "HSE Corrective Action", "link_fieldname": "incident", "group": "Follow-up"},
	],
)

doctype(
	"HSE Corrective Action",
	HSE,
	[
		"naming_series:Select:Series|opt=HSE-CA-.YYYY.-.####|reqd|default=HSE-CA-.YYYY.-.####|phide",
		"action:Small Text:Action|reqd|bold",
		"action_type:Select:Type|opt=Corrective\\nPreventive|default=Corrective|list",
		"priority:Select:Priority|opt=Low\\nMedium\\nHigh\\nCritical|default=Medium|list|filter",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd",
		"assigned_to:Link:Action Owner|opt=Employee|reqd",
		"assigned_to_name:Data:Owner Name|fetch=assigned_to.employee_name|ro|list",
		"due_date:Date:Due Date|reqd|list",
		"column_break_2:Column Break",
		"status:Select:Status|opt=Open\\nIn Progress\\nCompleted\\nVerified\\nCancelled|default=Open|list|filter",
		"is_overdue:Check:Overdue|ro|filter|nocopy",
		"source_section:Section Break:Raised From",
		"source:Select:Source|opt=\\nIncident\\nObservation\\nInspection\\nAudit\\nRisk Assessment\\nOther|list",
		"incident:Link:Incident|opt=HSE Incident|depends=eval:doc.source=='Incident'",
		"observation:Link:Observation|opt=HSE Observation|depends=eval:doc.source=='Observation'",
		"column_break_3:Column Break",
		"equipment_inspection:Link:Equipment Inspection|opt=Equipment Inspection|depends=eval:doc.source=='Inspection'",
		"risk_assessment:Link:Risk Assessment|opt=HSE Risk Assessment|depends=eval:doc.source=='Risk Assessment'",
		"closure_section:Section Break:Closure",
		"completed_on:Date:Completed On|nocopy",
		"completion_notes:Small Text:Completion Notes",
		"column_break_4:Column Break",
		"verified_by:Link:Verified By|opt=User|nocopy",
		"verified_on:Date:Verified On|nocopy",
		"evidence:Attach:Evidence",
	],
	autoname="naming_series:",
	title_field="action",
	search_fields="assigned_to_name,status,due_date",
	roles=STD,
	sort_field="due_date",
)

doctype(
	"HSE Observation",
	HSE,
	[
		"naming_series:Select:Series|opt=HSE-OBS-.YYYY.-.####|reqd|default=HSE-OBS-.YYYY.-.####|phide",
		"observation_type:Select:Type|opt=\\nUnsafe Act\\nUnsafe Condition\\nPositive Observation|reqd|list|filter",
		"category:Select:Category|opt=" + OBS_CATEGORIES + "|reqd|list|filter",
		"stop_work:Check:Work Stopped|desc=Stop Work Authority was used",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd",
		"observation_date:Date:Date|reqd|default=Today|list",
		"observed_by:Link:Observed By|opt=Employee",
		"observed_by_name:Data:Observer|fetch=observed_by.employee_name|ro|list",
		"column_break_2:Column Break",
		"status:Select:Status|opt=Open\\nClosed|default=Open|list|filter",
		"closed_on:Date:Closed On|nocopy",
		"where_section:Section Break:Where",
		"location:Link:Location|opt=Location|filter",
		"customer:Link:Client / Site Owner|opt=Customer",
		"column_break_3:Column Break",
		"asset:Link:Equipment|opt=Asset",
		"details_section:Section Break:Details",
		"description:Small Text:What Was Observed|reqd",
		"action_taken:Small Text:Action Taken on the Spot",
		"photo:Attach Image:Photo",
		"risk_section:Section Break:Risk|collapsible",
	]
	+ risk_block(),
	autoname="naming_series:",
	title_field="category",
	search_fields="observation_type,category,status",
	roles=REPORTABLE,
	sort_field="observation_date",
	image_field="photo",
	links=[
		{"link_doctype": "HSE Corrective Action", "link_fieldname": "observation", "group": "Follow-up"},
	],
)

# --------------------------------------------------------------------------- permits and risk

doctype(
	"HSE Risk Assessment Step",
	HSE,
	[
		"step:Data:Job Step|reqd|list|width=2",
		"hazard:Small Text:Hazard|reqd|list|width=2",
		"initial_likelihood:Int:L|list|width=1|desc=Likelihood 1-5 before controls",
		"initial_severity:Int:S|list|width=1|desc=Severity 1-5 before controls",
		"initial_score:Int:Risk|ro|list|width=1",
		"controls:Small Text:Control Measures|reqd|list|width=2",
		"residual_likelihood:Int:Residual L|desc=Likelihood 1-5 after controls",
		"residual_severity:Int:Residual S|desc=Severity 1-5 after controls",
		"residual_score:Int:Residual|ro|list|width=1",
		"responsible:Data:Responsible",
	],
	istable=True,
)

doctype(
	"HSE Risk Assessment",
	HSE,
	[
		"naming_series:Select:Series|opt=HSE-JSA-.YYYY.-.####|reqd|default=HSE-JSA-.YYYY.-.####|phide",
		"activity:Data:Activity|reqd|bold",
		"assessment_type:Select:Type|opt=Job Safety Analysis\\nTask Risk Assessment\\nSite Risk Assessment|default=Job Safety Analysis|list",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd",
		"assessment_date:Date:Assessment Date|reqd|default=Today|list",
		"review_date:Date:Review By",
		"column_break_2:Column Break",
		"location:Link:Location|opt=Location",
		"customer:Link:Client / Site Owner|opt=Customer",
		"prepared_by:Link:Prepared By|opt=Employee",
		"steps_section:Section Break:Job Steps and Hazards",
		"steps:Table:Steps|opt=HSE Risk Assessment Step|reqd",
		"summary_section:Section Break:Summary",
		"highest_initial_score:Int:Highest Initial Risk|ro",
		"highest_residual_score:Int:Highest Residual Risk|ro|list",
		"column_break_3:Column Break",
		"residual_risk_level:Select:Residual Risk Level|opt=" + RISK_LEVELS + "|ro|list|filter",
		"ppe_required:Small Text:PPE Required",
		"amended_from:Link:Amended From|opt=HSE Risk Assessment|ro|nocopy|phide",
	],
	autoname="naming_series:",
	is_submittable=True,
	title_field="activity",
	search_fields="assessment_type,residual_risk_level",
	roles=STD,
	sort_field="assessment_date",
	links=[
		{"link_doctype": "Permit to Work", "link_fieldname": "risk_assessment", "group": "Permits"},
		{"link_doctype": "HSE Corrective Action", "link_fieldname": "risk_assessment", "group": "Follow-up"},
	],
)

doctype(
	"HSE Permit Hazard",
	HSE,
	[
		"hazard:Data:Hazard|reqd|list|width=4",
		"control_measure:Small Text:Control Measure|reqd|list|width=5",
		"confirmed:Check:Done|list|width=1",
	],
	istable=True,
)

doctype(
	"HSE Gas Test",
	HSE,
	[
		"test_time:Datetime:Time|reqd|list|width=2",
		"oxygen_percent:Float:O2 %|list|width=1|precision=1",
		"lel_percent:Float:LEL %|list|width=1|precision=1",
		"h2s_ppm:Float:H2S ppm|list|width=1|precision=1",
		"co_ppm:Float:CO ppm|list|width=1|precision=1",
		"result:Select:Result|opt=\\nPass\\nFail|ro|list|width=1",
		"tested_by:Data:Tested By|list|width=3",
	],
	istable=True,
)

doctype(
	"Permit to Work",
	HSE,
	[
		"naming_series:Select:Series|opt=PTW-.YYYY.-.####|reqd|default=PTW-.YYYY.-.####|phide",
		"permit_type:Select:Permit Type|opt=\\nHot Work\\nCold Work\\nWorking at Height\\nConfined Space Entry"
		"\\nLifting Operation\\nExcavation\\nElectrical Isolation|reqd|list|filter",
		"work_description:Small Text:Work Description|reqd",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd",
		"location:Link:Location|opt=Location|reqd|filter",
		"customer:Link:Client / Site Owner|opt=Customer|filter",
		"project:Link:Project|opt=Project",
		"column_break_2:Column Break",
		"status:Select:Status|opt=Draft\\nRequested\\nApproved\\nActive\\nSuspended\\nClosed\\nRejected\\nExpired"
		"|default=Draft|ro|aos|list|filter|nocopy",
		"valid_from:Datetime:Valid From|reqd|list",
		"valid_to:Datetime:Valid To|reqd|list",
		"people_section:Section Break:Authorities",
		"performing_authority:Link:Performing Authority|opt=Employee|reqd|desc=Leads the crew doing the work",
		"performing_authority_name:Data:Performing Authority Name|fetch=performing_authority.employee_name|ro",
		"crew_size:Int:Crew Size",
		"column_break_3:Column Break",
		"issuing_authority:Link:Issuing Authority|opt=Employee|desc=Approves and issues the permit",
		"issuing_authority_name:Data:Issuing Authority Name|fetch=issuing_authority.employee_name|ro",
		"area_authority:Data:Area Authority (Client)",
		"risk_section:Section Break:Risk Controls",
		"risk_assessment:Link:Risk Assessment / JSA|opt=HSE Risk Assessment",
		"isolation_required:Check:Isolation Required",
		"isolation_details:Small Text:Isolation Details|depends=isolation_required",
		"column_break_4:Column Break",
		"ppe_required:Small Text:PPE Required",
		"fire_watch_required:Check:Fire Watch Required|depends=eval:doc.permit_type=='Hot Work'",
		"standby_person:Data:Standby / Hole Watch|depends=eval:doc.permit_type=='Confined Space Entry'",
		"hazards_section:Section Break:Hazards and Controls",
		"hazards:Table:Hazards|opt=HSE Permit Hazard",
		"gas_section:Section Break:Gas Testing|depends=gas_test_required",
		"gas_test_required:Check:Gas Test Required",
		"gas_tests:Table:Gas Tests|opt=HSE Gas Test|aos|depends=gas_test_required",
		"lifting_section:Section Break:Lifting Plan|depends=eval:doc.permit_type=='Lifting Operation'",
		"crane:Link:Crane|opt=Asset",
		"crane_name:Data:Crane Name|fetch=crane.asset_name|ro",
		"load_description:Data:Load",
		"load_weight_tonnes:Float:Load incl. Rigging (t)|precision=2",
		"column_break_lift:Column Break",
		"working_radius_m:Float:Working Radius (m)|precision=1",
		"capacity_at_radius_tonnes:Float:Crane Capacity at Radius (t)|precision=2",
		"utilisation_percent:Percent:Utilisation|ro",
		"is_critical_lift:Check:Critical Lift|ro|desc=Utilisation is above the threshold in HSE Settings",
		"lifting_plan:Attach:Lift Plan|mandatory_depends=is_critical_lift",
		"closure_section:Section Break:Closure|collapsible",
		"closed_on:Datetime:Closed On|aos|nocopy",
		"area_left_safe:Check:Work Area Left Safe|aos",
		"column_break_5:Column Break",
		"closure_remarks:Small Text:Closure Remarks|aos",
		"amended_from:Link:Amended From|opt=Permit to Work|ro|nocopy|phide",
	],
	autoname="naming_series:",
	is_submittable=True,
	title_field="permit_type",
	search_fields="permit_type,status,location",
	roles=STD,
	sort_field="valid_from",
)

# --------------------------------------------------------------------------- people

doctype(
	"HSE Competency",
	HSE,
	[
		"employee:Link:Employee|opt=Employee|reqd|list|filter",
		"employee_name:Data:Employee Name|fetch=employee.employee_name|ro|list|bold",
		"designation:Data:Designation|fetch=employee.designation|ro",
		"column_break_1:Column Break",
		"certificate_type:Link:Certificate|opt=HSE Certificate Type|reqd|list|filter",
		"certificate_no:Data:Certificate No",
		"issuing_body:Data:Issued By|fetch=certificate_type.issuing_body|if_empty=1",
		"column_break_2:Column Break",
		"issue_date:Date:Issue Date|reqd",
		"expiry_date:Date:Expiry Date|list",
		"status:Select:Status|opt=Valid\\nExpiring Soon\\nExpired|ro|list|filter",
		"attachment:Attach:Certificate Copy",
	],
	autoname="format:CMP-{employee}-{certificate_type}-{##}",
	naming_rule="Expression",
	title_field="employee_name",
	search_fields="employee_name,certificate_type,status",
	roles=STD,
	sort_field="expiry_date",
)

doctype(
	"Toolbox Talk Attendee",
	HSE,
	[
		"employee:Link:Employee|opt=Employee|reqd|list|width=3",
		"employee_name:Data:Name|fetch=employee.employee_name|ro|list|width=4",
		"designation:Data:Designation|fetch=employee.designation|ro|list|width=2",
		"signed:Check:Signed|list|width=1",
	],
	istable=True,
)

doctype(
	"Toolbox Talk",
	HSE,
	[
		"naming_series:Select:Series|opt=TBT-.YYYY.-.####|reqd|default=TBT-.YYYY.-.####|phide",
		"topic:Data:Topic|reqd|bold|list",
		"category:Select:Category|opt=" + OBS_CATEGORIES + "|filter",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd",
		"talk_date:Date:Date|reqd|default=Today|list",
		"duration_minutes:Int:Duration (Minutes)|default=15",
		"column_break_2:Column Break",
		"conducted_by:Link:Conducted By|opt=Employee|reqd",
		"conducted_by_name:Data:Presenter|fetch=conducted_by.employee_name|ro|list",
		"location:Link:Location|opt=Location",
		"attendees_section:Section Break:Attendees",
		"attendees:Table:Attendees|opt=Toolbox Talk Attendee|reqd",
		"attendee_count:Int:Attendees|ro|list",
		"notes_section:Section Break:Talk Notes",
		"key_points:Text Editor:Key Points",
		"questions_raised:Small Text:Questions Raised",
		"photo:Attach Image:Photo",
		"amended_from:Link:Amended From|opt=Toolbox Talk|ro|nocopy|phide",
	],
	autoname="naming_series:",
	is_submittable=True,
	title_field="topic",
	roles=STD,
	sort_field="talk_date",
)

doctype(
	"PPE Issue Item",
	HSE,
	[
		"item_code:Link:PPE Item|opt=Item|reqd|list|width=3",
		"item_name:Data:Item Name|fetch=item_code.item_name|ro|list|width=3",
		"size:Data:Size|list|width=1",
		"qty:Float:Qty|reqd|default=1|list|width=1",
		"uom:Link:UOM|opt=UOM|fetch=item_code.stock_uom|ro",
		"replace_by:Date:Replace By|list|width=2",
	],
	istable=True,
)

doctype(
	"PPE Issue",
	HSE,
	[
		"naming_series:Select:Series|opt=PPE-.YYYY.-.####|reqd|default=PPE-.YYYY.-.####|phide",
		"employee:Link:Employee|opt=Employee|reqd|list|filter",
		"employee_name:Data:Employee Name|fetch=employee.employee_name|ro|list|bold",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd",
		"issue_date:Date:Issue Date|reqd|default=Today|list",
		"issue_reason:Select:Reason|opt=New Joiner\\nReplacement\\nDamaged\\nLost\\nVisitor|default=New Joiner",
		"column_break_2:Column Break",
		"acknowledged:Check:Received and Acknowledged by Employee",
		"stock_entry:Link:Stock Entry|opt=Stock Entry|ro|nocopy",
		"items_section:Section Break:PPE Items",
		"items:Table:Items|opt=PPE Issue Item|reqd",
		"amended_from:Link:Amended From|opt=PPE Issue|ro|nocopy|phide",
	],
	autoname="naming_series:",
	is_submittable=True,
	title_field="employee_name",
	roles=STD,
	sort_field="issue_date",
)

# --------------------------------------------------------------------------- equipment

doctype(
	"Equipment Inspection Reading",
	HSE,
	[
		"check_item:Data:Check Item|reqd|list|width=4",
		"category:Data:Category|list|width=2",
		"is_critical:Check:Critical|ro|list|width=1",
		"result:Select:Result|opt=\\nPass\\nFail\\nN/A|reqd|list|width=1",
		"remarks:Data:Remarks|list|width=2",
	],
	istable=True,
)

doctype(
	"Equipment Inspection",
	HSE,
	[
		"naming_series:Select:Series|opt=EQI-.YYYY.-.####|reqd|default=EQI-.YYYY.-.####|phide",
		"asset:Link:Equipment|opt=Asset|reqd|list|filter",
		"asset_name:Data:Equipment Name|fetch=asset.asset_name|ro|list|bold",
		"asset_category:Link:Asset Category|opt=Asset Category|fetch=asset.asset_category|ro|filter",
		"column_break_1:Column Break",
		"company:Link:Company|opt=Company|reqd|fetch=asset.company|if_empty=1",
		"inspection_type:Select:Inspection Type|opt=\\nPre-Use Check\\nPeriodic Inspection\\nThird-Party Certification\\nLoad Test|reqd|list|filter",
		"inspection_date:Date:Inspection Date|reqd|default=Today|list",
		"template:Link:Checklist Template|opt=HSE Inspection Template",
		"column_break_2:Column Break",
		"result:Select:Result|opt=\\nPass\\nPass with Observations\\nFail|list|filter",
		"inspected_by:Link:Inspected By|opt=Employee",
		"meter_reading:Float:Hour / Km Meter",
		"certificate_section:Section Break:Certification",
		"inspection_agency:Link:Third-Party Agency|opt=Supplier",
		"certificate_no:Data:Certificate No",
		"column_break_3:Column Break",
		"certificate_expiry:Date:Certificate Valid Until|list",
		"next_inspection_due:Date:Next Inspection Due",
		"certificate_file:Attach:Certificate Copy",
		"readings_section:Section Break:Checklist",
		"readings:Table:Checklist|opt=Equipment Inspection Reading",
		"remarks_section:Section Break",
		"remarks:Small Text:Remarks",
		"amended_from:Link:Amended From|opt=Equipment Inspection|ro|nocopy|phide",
	],
	autoname="naming_series:",
	is_submittable=True,
	title_field="asset_name",
	search_fields="asset_name,inspection_type,result",
	roles=STD,
	sort_field="inspection_date",
	links=[
		{
			"link_doctype": "HSE Corrective Action",
			"link_fieldname": "equipment_inspection",
			"group": "Follow-up",
		},
	],
)

# --------------------------------------------------------------------------- journeys

doctype(
	"Journey Checkpoint",
	HSE,
	[
		"checkpoint:Data:Checkpoint / Rest Stop|reqd|list|width=3",
		"planned_time:Datetime:Planned|list|width=2",
		"actual_time:Datetime:Actual|list|width=2",
		"remarks:Data:Remarks|list|width=3",
	],
	istable=True,
)

doctype(
	"Journey Management Plan",
	HSE,
	[
		"naming_series:Select:Series|opt=JMP-.YYYY.-.####|reqd|default=JMP-.YYYY.-.####|phide",
		"company:Link:Company|opt=Company|reqd",
		"vehicle:Link:Vehicle / Tanker|opt=Asset|reqd|list",
		"vehicle_name:Data:Vehicle Name|fetch=vehicle.asset_name|ro",
		"vehicle_no:Data:Plate No",
		"column_break_1:Column Break",
		"driver:Link:Driver|opt=Employee|reqd",
		"driver_name:Data:Driver Name|fetch=driver.employee_name|ro|list|bold",
		"journey_manager:Link:Journey Manager|opt=Employee",
		"column_break_2:Column Break",
		"status:Select:Status|opt=Planned\\nApproved\\nIn Transit\\nArrived\\nCancelled|default=Planned|list|filter",
		"customer:Link:Client|opt=Customer|filter",
		"cargo:Data:Cargo / Load",
		"route_section:Section Break:Route",
		"from_location:Data:From|reqd|list",
		"to_location:Data:To|reqd|list",
		"distance_km:Float:Distance (km)|precision=0",
		"route_notes:Small Text:Route Hazards and Notes",
		"column_break_3:Column Break",
		"planned_departure:Datetime:Planned Departure|reqd|list",
		"planned_arrival:Datetime:Planned Arrival",
		"actual_departure:Datetime:Actual Departure|nocopy",
		"actual_arrival:Datetime:Actual Arrival|nocopy",
		"checks_section:Section Break:Pre-Journey Checks",
		"vehicle_inspected:Check:Vehicle Pre-Trip Inspection Done",
		"ivms_working:Check:IVMS Working",
		"column_break_4:Column Break",
		"driver_rested:Check:Driver Fit and Rested (Fatigue Declaration)",
		"night_driving:Check:Night Driving|desc=Needs journey manager approval",
		"driver_certificate_valid:Check:Driver Certificate Valid|ro|nocopy",
		"checkpoints_section:Section Break:Checkpoints and Rest Stops",
		"checkpoints:Table:Checkpoints|opt=Journey Checkpoint",
	],
	autoname="naming_series:",
	title_field="driver_name",
	search_fields="driver_name,vehicle,status",
	roles=STD,
	sort_field="planned_departure",
)

print("HSE doctypes written")
