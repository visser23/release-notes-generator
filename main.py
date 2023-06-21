import requests
from docx import Document

def generate_release_notes(request):
    payload = request.json
    released_fix_version = payload['fixVersion']['name']
    logo_url = "https://nhshealthcall.co.uk/wp-content/themes/health_call_2022/images/logo_health_call.png"

    # Retrieve issue details from Jira
    jira_issues_url = f"https://servita-uk.atlassian.net/jira/rest/api/2/search"
    jira_headers = {
        "Authorization": "Bearer ATATT3xFfGF0h1WuFZJy9jXFViCDlYVYILzWtqukLDHbEH2_KJIeP2zMx5m4yF2ENPYnUkMfaRRw9pSgDx8bdS3DH_bqAGglcsIF8RetSA4CxR2DSxIvmJXap-xrarRh4lyigKPnF-fyV75L34pyuedQws8Nv9RLXqwePRCz3BjuA_eQ16aDYJ0=5A479038",
        "Content-Type": "application/json"
    }
    jira_payload = {
        "jql": f"fixVersion = '{released_fix_version}'",
        "fields": "summary"
    }
    jira_response = requests.get(jira_issues_url, headers=jira_headers, json=jira_payload)
    issues = jira_response.json().get("issues", [])

    # Generate the release notes document
    doc = Document()
    doc.add_picture(logo_url)
    doc.add_heading(f"Release Notes - {released_fix_version}", level=1)
    for issue in issues:
        summary = issue["fields"]["summary"]
        doc.add_heading(summary, level=2)

    # Save and upload the release notes document to Confluence
    doc.save("/tmp/release_notes.docx")
    confluence_url = "https://servita-uk.atlassian.net/wiki/rest/api/content/139853825/child/attachment"
    confluence_headers = {
        "Authorization": "Bearer ATATT3xFfGF0h1WuFZJy9jXFViCDlYVYILzWtqukLDHbEH2_KJIeP2zMx5m4yF2ENPYnUkMfaRRw9pSgDx8bdS3DH_bqAGglcsIF8RetSA4CxR2DSxIvmJXap-xrarRh4lyigKPnF-fyV75L34pyuedQws8Nv9RLXqwePRCz3BjuA_eQ16aDYJ0=5A479038",
        "X-Atlassian-Token": "no-check"
    }
    confluence_params = {
        "minorEdit": "true"
    }
    confluence_files = {
        "file": open("/tmp/release_notes.docx", "rb")
    }
    confluence_response = requests.post(confluence_url, headers=confluence_headers, params=confluence_params, files=confluence_files)

    if confluence_response.status_code == 200:
        return {"message": "Release notes generated and uploaded successfully."}
    else:
        return {"message": "Failed to upload release notes."}

# Vercel API route
def webhook(request):
    if request.method == "POST":
        return generate_release_notes(request)
    else:
        return {"message": "Invalid request method."}
