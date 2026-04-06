import urllib.request
import json
import sys

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        m = req.get_method()
        if (not (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m == "POST")):
            raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)
        new_req = urllib.request.Request(
            newurl,
            headers=req.headers,
            origin_req_host=req.origin_req_host,
            unverifiable=True,
            method=m
        )
        # Remove authorization header so S3 doesn't get confused
        if 'Authorization' in new_req.headers:
            del new_req.headers['Authorization']
        if 'authorization' in new_req.headers:
            del new_req.headers['authorization']
        return new_req

token = "YOUR_GITHUB_TOKEN_HERE"
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
opener = urllib.request.build_opener(NoAuthRedirectHandler)
urllib.request.install_opener(opener)

req = urllib.request.Request("https://api.github.com/repos/Makairamei/CS01/actions/runs?per_page=1", headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        run_id = res['workflow_runs'][0]['id']
        jobs_url = res['workflow_runs'][0]['jobs_url']
except Exception as e:
    sys.exit(1)

req = urllib.request.Request(jobs_url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        jobs = json.loads(response.read().decode())['jobs']
        job_id = jobs[0]['id']
except Exception as e:
    sys.exit(1)

log_url = f"https://api.github.com/repos/Makairamei/CS01/actions/jobs/{job_id}/logs"
req = urllib.request.Request(log_url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        log_content = response.read().decode()
except Exception as e:
    print(f"Failed to fetch logs: {e}")
    sys.exit(1)

lines = log_content.split('\n')
print('\n'.join(lines[-200:]))
