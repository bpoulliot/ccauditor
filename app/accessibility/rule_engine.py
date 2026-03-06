from app.accessibility.remediation import remediation_guidance


def evaluate_rules(issues):

    results = []

    for issue in issues:

        guidance = remediation_guidance.get(issue["type"], "")

        results.append({
            "type": issue["type"],
            "severity": issue.get("severity", "medium"),
            "location": issue.get("location"),
            "guidance": guidance,
        })

    return results