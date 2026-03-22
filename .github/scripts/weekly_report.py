import os
from datetime import datetime, timedelta
from github import Github

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    report_issue_num = int(os.getenv("REPORT_ISSUE_NUMBER", "1"))

    g = Github(token)
    repo = g.get_repo(repo_name)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Получаем закрытые issues за последние 7 дней
    closed_issues = repo.get_issues(state='closed', since=start_date)

    report_lines = []
    report_lines.append(f"# Weekly Report: {start_date.strftime('%Y-%m-%d')} – {end_date.strftime('%Y-%m-%d')}")
    report_lines.append("")
    report_lines.append("| # | Задача | Дата закрытия | Связанные PR |")
    report_lines.append("|---|--------|----------------|--------------|")

    for issue in closed_issues:
        if issue.pull_request:  # пропускаем сами PR, только задачи
            continue

        # Ищем PR, которые закрыли этот issue (по строке "Closes #<номер>" в теле)
        prs = repo.get_pulls(state='closed', sort='updated')
        related_prs = []
        for pr in prs:
            if pr.body and f"Closes #{issue.number}" in pr.body:
                related_prs.append(pr)
        pr_links = ", ".join([f"[#{pr.number}]({pr.html_url})" for pr in related_prs]) if related_prs else "—"

        report_lines.append(f"| #{issue.number} | {issue.title} | {issue.closed_at.strftime('%Y-%m-%d')} | {pr_links} |")

    report_body = "\n".join(report_lines)

    # Добавляем комментарий к issue отчёта
    report_issue = repo.get_issue(number=report_issue_num)
    report_issue.create_comment(report_body)

if __name__ == "__main__":
    main()
