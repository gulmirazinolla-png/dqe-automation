# PyTest Introduction + Report Portal

## Setup
pip install -r requirements.txt

## Run locally
pytest -v

## Run with Report Portal
Set the API key (never commit it):
- PowerShell: $env:RP_API_KEY="<your_key>"
- Bash: export RP_API_KEY=<your_key>

pytest --reportportal --runxfail -v

`--runxfail` is used so the expected failures (malformed email, duplicate row)
are reported as failed in Report Portal and can be analysed with defect types.

Report Portal settings are in `pytest.ini` (rp_endpoint, rp_project, rp_launch, ...).