<img src="assets/icon.svg" width="64" height="64" alt="">

# Frappe HSE

Health, Safety and Environment management for ERPNext v16, built for contractors in oil and gas, construction, logistics and equipment hire. Report incidents and follow them to closure, issue permits to work, keep equipment certified, and keep drivers and operators competent. The HSE statistics your clients ask for (LTIFR, TRIR, days since the last LTI) are worked out for you.

## What it covers

| Area | Documents |
|---|---|
| Incidents | **HSE Incident** with injured persons, potential risk, investigation, 5-Why and root cause. Status moves from Reported to Under Investigation to Actions Open to Closed on its own. |
| Corrective actions | **HSE Corrective Action** raised from incidents, observations, inspections or risk assessments, with an owner, a due date, overdue flags and verification. |
| Observations | **HSE Observation** cards for unsafe acts and conditions, positive observations and Stop Work Authority. Any employee can raise one. |
| Safe work | **Permit to Work** (hot work, confined space, working at height, lifting, excavation, electrical isolation) with an approval workflow, gas tests (O2 / LEL / H2S / CO checked against limits), and lift plans that flag critical lifts. **HSE Risk Assessment** (JSA) uses a 5x5 risk matrix and blocks approval while residual risk is still Extreme. **Toolbox Talk** records attendance and sign-off. |
| Equipment | **Equipment Inspection** covers pre-use checks, periodic and third-party inspections and load tests, using checklist templates. The result and certificate expiry are copied onto the Asset as **Fit for Use**. |
| Journeys | **Journey Management Plan** for tankers and heavy vehicles. It checks the pre-trip inspection, IVMS and fatigue declaration, the driver's certificate and the vehicle's fitness, and night driving needs journey manager approval. |
| People | **HSE Competency** tracks each employee's certificates (defensive driving, H2S, crane operator, rigger, first aid...), with expiry alerts. **PPE Issue** can post a stock Material Issue from the PPE store. |
| Statistics | **HSE Manhours** per month feed the **HSE Statistics** report (LTIFR, TRIR, days lost, vehicle incidents, spills, observations, toolbox talks). The **Certificate Expiry Register** lists people and equipment together. |

The HSE workspace and dashboard show days since the last LTI, open incidents, active permits, overdue actions, expiring certificates and equipment that is not fit for use.

### Works with ERPNext Asset Leasing

When [ERPNext Asset Leasing](https://github.com/skyasir/erpnext_asset_leasing) is installed:

- a **Rental Dispatch** cannot be submitted for equipment that failed its last inspection or whose certificate has expired
- a **Wet Hire** Rental Agreement cannot be submitted unless the operator holds a valid operator certificate

Both rules can be switched off in **HSE Settings**.

## Installation

```bash
bench get-app https://github.com/skyasir/frappe-hse
bench --site your-site install-app frappe_hse
```

Requires Frappe and ERPNext v16. The install creates the HSE roles (HSE Manager, HSE Officer, HSE User), the HSE fields on Asset, the Permit to Work approval workflow, common oil and gas certificate types and pre-use checklists for cranes, forklifts and tankers.

## Setup

1. Open **HSE Settings**. Set the HSE manager, the frequency base (1,000,000 man-hours for OPAL / PDO style reporting, 200,000 for OSHA), and the driver and operator certificates to check.
2. Review the **HSE Certificate Types** and **HSE Inspection Templates** and add your own.
3. Give users the **HSE Manager**, **HSE Officer** or **HSE User** role. Every employee can already raise observations and report incidents.
4. Enter the monthly **HSE Manhours** so the frequency rates can be worked out.

## License

GNU General Public License v3.0

<!-- portfolio:start -->
---

<p align="center">
  <a href="https://yasirshaikh.in/?app=frappe-hse">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://yasirshaikh.in/files/yasir-logo-on-dark.svg">
      <img src="https://yasirshaikh.in/files/yasir-logo.svg" alt="Yasir Shaikh" height="64">
    </picture>
  </a>
</p>

<p align="center">
  Built by <a href="https://yasirshaikh.in/">Yasir Shaikh</a>, ERPNext consultant and Frappe developer.<br>
  <a href="https://yasirshaikh.in/?app=frappe-hse">See this app on my portfolio</a>
</p>
<!-- portfolio:end -->
