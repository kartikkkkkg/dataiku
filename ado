Initiative
└── TTO Central Reserve Initiative (Already exists)

    └── Epic
        Workforce Management Dashboard Automation

            └── Feature
                HCMT Dashboard

                    ├── Generic Task
                    │   Create HC Data Pipeline
                    │
                    ├── Generic Task
                    │   Build Actual Headcount Dataset
                    │
                    ├── Generic Task
                    │   Build Joiners Dataset
                    │
                    ├── Generic Task
                    │   Build Leavers Dataset
                    │
                    ├── Generic Task
                    │   Build Transfers Dataset
                    │
                    ├── Generic Task
                    │   Build Fieldglass Dataset
                    │
                    ├── Generic Task
                    │   Build Job Requisition Dataset
                    │
                    ├── Generic Task
                    │   Implement Mapping Logic
                    │
                    ├── Generic Task
                    │   Implement Include/Exclude Rules
                    │
                    ├── Generic Task
                    │   Dashboard Validation & Testing
                    │
                    └── Generic Task
                        Production Deployment


Feature

HCMT Dashboard

Description

Develop the HCMT Dashboard by integrating Actuals, Joiners, Leavers, Transfers, Fieldglass, Job Requisitions, and mapping datasets. Implement business rules, data quality checks, reconciliation logic, and dashboard outputs for Workforce Management reporting.

Generic Tasks
1. Create HC Data Pipeline
Configure Dataiku flow
Build input datasets
Configure joins
2. Build Actual Headcount Dataset
Headcount preparation
Rollup mapping
Cost category mapping
MT Domain mapping
3. Build Joiners Dataset
Prepare Joiners dataset
Position validation
Future joiner handling
Duplicate handling
4. Build Leavers Dataset
Prepare Leavers dataset
Effective date validation
Reporting logic
5. Build Transfers Dataset
Same Domain validation
Same Cost validation
Prior month exclusion
Future effective year exclusion
6. Build Fieldglass Dataset
MOW/MSW exclusion
Duplicate Position ID handling
Position validation
7. Build Job Requisition Dataset
JR preparation
Position ID mapping
FG/JR reconciliation
8. Implement Mapping Logic
MT Domain
MT-1 Domain
Cost Category
Rollup hierarchy
Controllable / Non-Controllable
9. Implement Include / Exclude Logic
Blank Position ID
Duplicate removal
MOW/MSW exclusion
Future date checks
Include/Exclude status generation
10. Dashboard Validation & Testing
Dataset validation
Business rule verification
UAT support
Defect fixes
11. Production Deployment
Deploy Dataiku flow
Validate production outputs
Production support
Documentation
