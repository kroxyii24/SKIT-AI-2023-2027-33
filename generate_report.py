import subprocess
from collections import defaultdict
import datetime
import io
import os
import sys
import html

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

COLLEGE_NAME = "Swami Keshvanand Institute of Technology,Management & Gramothan, Jaipur"
DEPARTMENT_NAME = "Department of Computer Science & Engineering"


def get_repo_info():
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        repo_name = os.path.basename(root)
    except Exception:
        repo_name = os.path.basename(os.getcwd())

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
    except Exception:
        branch = "unknown"

    return repo_name, branch


def get_git_metrics(interval="weekly"):
    today = datetime.date.today()
    args = [
        "git", "log", "--no-merges",
        "--pretty=format:COMMIT|||%h|||%an|||%ad|||%s",
        "--date=short", "--numstat"
    ]

    if interval == "weekly":
        since = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        args.append(f"--since={since}")
        scope = f"Last 7 Days (Since {since})"
    elif interval == "monthly":
        since = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        args.append(f"--since={since}")
        scope = f"Last 30 Days (Since {since})"
    elif interval == "final":
        scope = "Complete Project Lifecycle (All Commits)"
    else:
        raise ValueError("Use weekly, monthly, or final.")

    try:
        output = subprocess.check_output(
            args, text=True, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Git command failed: {exc.stderr}")
        return None, None, None, scope

    students = defaultdict(
        lambda: {
            "commits": 0, "added": 0, "deleted": 0, "active_days": set()
        }
    )
    timeline = defaultdict(lambda: defaultdict(int))
    logs = defaultdict(list)
    author = None

    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.startswith("COMMIT|||"):
            parts = line.split("|||", 4)
            if len(parts) < 5:
                author = None
                continue

            _, sha, name, date_str, message = parts
            if (
                "bot" in name.lower()
                or "github-actions" in name.lower()
                or name.strip().casefold() not in {
                    "eklavya gupta", "gagan sharma"
                }
            ):
                author = None
                continue

            author = name
            students[author]["commits"] += 1
            students[author]["active_days"].add(date_str)
            logs[author].append((date_str, sha, message))

            try:
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if interval == "weekly":
                    period = dt.strftime("%a (%b %d)")
                elif interval == "monthly":
                    period = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
                else:
                    period = dt.strftime("%Y-%m")
                timeline[period][author] += 1
            except ValueError:
                pass

        elif author:
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                students[author]["added"] += int(parts[0])
                students[author]["deleted"] += int(parts[1])

    return students, timeline, logs, scope


def create_chart(students, timeline, interval):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    authors = list(students)
    periods = sorted(timeline)

    if periods and authors:
        for author in authors:
            counts = [timeline[p].get(author, 0) for p in periods]
            ax1.plot(periods, counts, marker="o", linewidth=2, label=author)
        ax1.set_title(f"Commit Timeline ({interval.capitalize()})")
        ax1.set_ylabel("Commits")
        ax1.tick_params(axis="x", rotation=30)
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(fontsize=7)
    else:
        ax1.text(0.5, 0.5, "No commits found", ha="center", va="center")
        ax1.set_axis_off()

    if authors:
        net = [students[a]["added"] - students[a]["deleted"] for a in authors]
        ax2.bar(authors, net, width=0.5)
        ax2.set_title("Net Lines of Code")
        ax2.set_ylabel("Added minus deleted")
        ax2.tick_params(axis="x", rotation=25)
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
    else:
        ax2.text(0.5, 0.5, "No line changes recorded", ha="center", va="center")
        ax2.set_axis_off()

    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return Image(buffer, width=500, height=175)


def generate_pdf(interval="weekly"):
    repo, branch = get_repo_info()
    students, timeline, logs, scope = get_git_metrics(interval)

    if students is None:
        return

    today = datetime.date.today().strftime("%Y-%m-%d")
    if interval == "weekly":
        title = "Weekly Progress Report (Form-3)"
        filename = f"{repo}_Weekly_Progress_Report_Form-3_{today}.pdf"
    elif interval == "monthly":
        title = "Monthly Progress Report (Form-3)"
        filename = f"{repo}_Monthly_Progress_Report_Form-3_{today}.pdf"
    else:
        title = "Final Project Evaluation Report"
        filename = f"{repo}_Final_Report_{today}.pdf"

    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=30, bottomMargin=30
    )

    styles = getSampleStyleSheet()
    college = ParagraphStyle(
        "College", parent=styles["Heading1"], fontSize=13,
        leading=16, alignment=1, textColor=colors.HexColor("#0F172A")
    )
    department = ParagraphStyle(
        "Department", parent=styles["Normal"], fontSize=9,
        alignment=1, textColor=colors.HexColor("#475569"), spaceAfter=6
    )
    heading = ParagraphStyle(
        "ReportTitle", parent=styles["Heading2"], fontSize=13,
        alignment=1, textColor=colors.HexColor("#1A365D"), spaceAfter=8
    )
    section = ParagraphStyle(
        "Section", parent=styles["Heading2"], fontSize=10,
        spaceBefore=7, spaceAfter=4
    )
    subsection = ParagraphStyle(
        "Subsection", parent=styles["Heading3"], fontSize=9,
        textColor=colors.HexColor("#2563EB"), spaceBefore=5, spaceAfter=3
    )
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=7.5, leading=9)
    centered = ParagraphStyle(
        "Centered", parent=small, alignment=1
    )
    signature = ParagraphStyle(
        "Signature", parent=styles["Normal"], fontSize=9, leading=15
    )

    story = [
        Paragraph(f"<b>{html.escape(COLLEGE_NAME)}</b>", college),
        Paragraph(f"<b>{html.escape(DEPARTMENT_NAME)}</b>", department),
        Paragraph(f"<u><b>{html.escape(title)}</b></u>", heading),
        Paragraph(
            f"<b>Project Repository:</b> {html.escape(repo)} &nbsp;|&nbsp; "
            f"<b>Branch:</b> {html.escape(branch)}",
            styles["Normal"]
        ),
        Paragraph(
            f"<b>Evaluation Window:</b> {html.escape(scope)} &nbsp;|&nbsp; "
            f"<b>Generated On:</b> {datetime.date.today():%B %d, %Y}",
            small
        ),
        Spacer(1, 6),
        Paragraph("1. Individual Contribution Breakdown", section),
    ]

    total_commits = sum(v["commits"] for v in students.values())
    data = [[
        "Student Name", "Commits (%)", "Lines Added",
        "Lines Deleted", "Net LOC", "Active Days"
    ]]

    for name, values in students.items():
        pct = values["commits"] / total_commits * 100 if total_commits else 0
        data.append([
            Paragraph(html.escape(name), small),
            f"{values['commits']} ({pct:.1f}%)",
            f"+{values['added']:,}",
            f"-{values['deleted']:,}",
            f"{values['added'] - values['deleted']:,}",
            str(len(values["active_days"]))
        ])

    if not students:
        data.append(["No commits found for this period", "-", "-", "-", "-", "-"])

    table = Table(data, colWidths=[120, 80, 80, 80, 80, 80], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    story.extend([
        table, Spacer(1, 6),
        Paragraph("2. Visual Trends & Volume", section),
        create_chart(students, timeline, interval),
        Spacer(1, 6),
        Paragraph(
            f"3. Detailed Commit Logs & Mentor Evaluation ({interval.capitalize()})",
            section
        )
    ])

    if not logs:
        story.append(Paragraph("No commit logs found for this timeframe.", styles["Normal"]))
    else:
        for author, entries in logs.items():
            group = [
                Paragraph(
                    f"<b>Student:</b> {html.escape(author)} — "
                    f"<i>{len(entries)} commit(s)</i>",
                    subsection
                )
            ]
            rows = [["Date", "Hash", "Commit Message", "Mentor Marks (/10)"]]
            for index, (date, sha, message) in enumerate(entries):
                marks = Paragraph("<b>_____ / 10</b>", centered) if index == 0 else ""
                rows.append([
                    Paragraph(html.escape(date), centered),
                    Paragraph(html.escape(sha), centered),
                    Paragraph(html.escape(message or "(No commit message)"), small),
                    marks
                ])

            log_table = Table(rows, colWidths=[65, 50, 335, 90], repeatRows=1)
            style = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
            if len(rows) > 1:
                style.extend([
                    ("SPAN", (3, 1), (3, len(rows) - 1)),
                    ("VALIGN", (3, 1), (3, len(rows) - 1), "MIDDLE"),
                    ("BACKGROUND", (3, 1), (3, len(rows) - 1), colors.HexColor("#FEF3C7")),
                ])
            log_table.setStyle(TableStyle(style))
            group.extend([log_table, Spacer(1, 5)])
            story.append(KeepTogether(group))

    story.extend([
        Spacer(1, 16),
        Table([[
            [
                Paragraph("<b>Name:</b> ___________________________", signature),
                Paragraph("<b>Designation:</b> Project Mentor", signature),
                Spacer(1, 6),
                Paragraph("<b>Signature:</b> ________________________", signature),
            ],
            [
                Paragraph("<b>Name:</b> ___________________________", signature),
                Paragraph("<b>Designation:</b> Lab Coordinator", signature),
                Spacer(1, 6),
                Paragraph("<b>Signature:</b> ________________________", signature),
            ]
        ]], colWidths=[270, 270])
    ])

    doc.build(story)
    print(f"\n[SUCCESS] Generated: {filename}")
    print(f"Found {len(students)} contributor(s) and {total_commits} total commits.")


def get_git_metrics_for_dates(start_date, end_date):
    args = [
        "git", "log", "--no-merges",
        "--pretty=format:COMMIT|||%h|||%an|||%ad|||%s",
        "--date=short", "--numstat",
        f"--since={start_date.isoformat()} 00:00:00",
        f"--until={end_date.isoformat()} 23:59:59",
    ]
    output = subprocess.check_output(args, text=True, stderr=subprocess.PIPE)
    students = defaultdict(lambda: {
        "commits": 0, "added": 0, "deleted": 0, "active_days": set()
    })
    timeline = defaultdict(lambda: defaultdict(int))
    logs = defaultdict(list)
    author = None

    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("COMMIT|||"):
            parts = line.split("|||", 4)
            if len(parts) < 5:
                author = None
                continue
            _, sha, name, date_str, message = parts
            if (
                "bot" in name.lower()
                or "github-actions" in name.lower()
                or name.strip().casefold() not in {
                    "eklavya gupta", "gagan sharma"
                }
            ):
                author = None
                continue
            author = name
            students[author]["commits"] += 1
            students[author]["active_days"].add(date_str)
            logs[author].append((date_str, sha, message))
            timeline[date_str][author] += 1
        elif author:
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                students[author]["added"] += int(parts[0])
                students[author]["deleted"] += int(parts[1])

    scope = f"{start_date:%d %b %Y} - {end_date:%d %b %Y}"
    return students, timeline, logs, scope


def generate_historical_reports(start_date, end_date):
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    if end < start:
        raise ValueError("End date must not be earlier than start date.")

    output_dir = os.path.join(os.getcwd(), "weekly_reports")
    os.makedirs(output_dir, exist_ok=True)
    repo, _ = get_repo_info()
    current = start
    week_number = 1

    while current <= end:
        period_end = min(current + datetime.timedelta(days=6), end)
        print(f"\nGenerating Week {week_number}: {current} to {period_end}")

        original_metrics = get_git_metrics

        def period_metrics(interval="weekly", _start=current, _end=period_end):
            return get_git_metrics_for_dates(_start, _end)

        globals()["get_git_metrics"] = period_metrics
        try:
            generate_pdf("weekly")
        finally:
            globals()["get_git_metrics"] = original_metrics

        generated_date = datetime.date.today().isoformat()
        default_name = f"{repo}_Weekly_Progress_Report_Form-3_{generated_date}.pdf"
        if os.path.exists(default_name):
            destination = os.path.join(
                output_dir,
                f"Week_{week_number:02d}_{current:%d%b}_{period_end:%d%b}_{period_end:%Y}.pdf"
            )
            os.replace(default_name, destination)
            print(f"[SAVED] {destination}")

        current = period_end + datetime.timedelta(days=1)
        week_number += 1

if __name__ == "__main__":
    interval = sys.argv[1].lower() if len(sys.argv) > 1 else "weekly"
    if interval == "history":
        start = sys.argv[2] if len(sys.argv) > 2 else "2026-10-09"
        end = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().isoformat()
        generate_historical_reports(start, end)
    else:
        generate_pdf(interval)
