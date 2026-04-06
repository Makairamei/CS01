import urllib.request
import json
import sys

token = "YOUR_GITHUB_TOKEN_HERE"
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

# Get latest run
req = urllib.request.Request("https://api.github.com/repos/Makairamei/CS01/actions/runs?per_page=1", headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        if not res['workflow_runs']:
            print("No workflow runs found.")
            sys.exit(1)
        run_id = res['workflow_runs'][0]['id']
        jobs_url = res['workflow_runs'][0]['jobs_url']
except Exception as e:
    print(f"Failed to fetch runs: {e}")
    sys.exit(1)

# Get jobs for the run
req = urllib.request.Request(jobs_url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        jobs = json.loads(response.read().decode())['jobs']
        if not jobs:
            print("No jobs found.")
            sys.exit(1)
        job_id = jobs[0]['id']
except Exception as e:
    print(f"Failed to fetch jobs: {e}")
    sys.exit(1)

# Get logs for the job
log_url = f"https://api.github.com/repos/Makairamei/CS01/actions/jobs/{job_id}/logs"
req = urllib.request.Request(log_url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        log_content = response.read().decode()
except urllib.error.HTTPError as e:
    # A redirect might happen
    if e.code in (301, 302, 307, 308):
        redirect_url = e.headers.get('Location')
        req = urllib.request.Request(redirect_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            log_content = response.read().decode()
    else:
        print(f"Failed to fetch logs: {e}")
        sys.exit(1)

# print the last 150 lines of logs as errors are usually at the end
lines = log_content.split('\n')
print('\n'.join(lines[-150:]))
