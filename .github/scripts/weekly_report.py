import os
from datetime import datetime, timedelta
from github import Github

def format_pr_info(pr):
    """Форматирует информацию о PR: ссылка, заголовок, описание."""
    header = f"[#{pr.number}]({pr.html_url}) — {pr.title}"
    body = pr.body or ""
    if body:
        # Убираем лишние переносы, обрезаем
        body = body.strip().replace('\n', ' ')
        if len(body) > 200:
            body = body[:200] + "..."
        return f"{header}\n  > {body}"
    else:
        return header

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    report_issue_num = int(os.getenv("REPORT_ISSUE_NUMBER", "1"))

    g = Github(token)
    repo = g.get_repo(repo_name)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    closed_issues = repo.get_issues(state='closed', since=start_date)

    report_lines = []
    report_lines.append(f"# Weekly Report: {start_date.strftime('%Y-%m-%d')} – {end_date.strftime('%Y-%m-%d')}")
    report_lines.append("")
    report_lines.append("| # | Задача | Дата закрытия | Описание |")
    report_lines.append("|---|--------|----------------|----------|")

    for issue in closed_issues:
        if issue.pull_request:
            continue  # пропускаем сами PR

        # Находим PR, которые закрыли этот issue
        prs = repo.get_pulls(state='closed', sort='updated')
        related_prs = []
        for pr in prs:
            if pr.body and f"Closes #{issue.number}" in pr.body:
                related_prs.append(pr)

        if related_prs:
            pr_info = "<br>".join([format_pr_info(pr) for pr in related_prs])
        else:
            pr_info = "—"

        report_lines.append(f"| #{issue.number} | {issue.title} | {issue.closed_at.strftime('%Y-%m-%d')} | {pr_info} |")

    report_body = "\n".join(report_lines)

    report_issue = repo.get_issue(number=report_issue_num)
    report_issue.create_comment(report_body)

if __name__ == "__main__":
    main()
