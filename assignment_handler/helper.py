from assignment_handler.models import Project
from typing import List, Tuple, Union


def calculate_average_progress(projects: List[Project]) -> float:
    total_progress = 0
    total_projects = len(projects)

    if total_projects == 0:
        return 0.00

    for project in projects:
        total_progress += project.get_project_progress()

    average_progress = total_progress / total_projects
    return average_progress


def budget_status_completed(projects: List[Project]) -> Tuple[str, float]:
    if not projects:
        return "There are no completed projects", False

    total_budget = 0
    total_used = 0

    for project in projects:
        total_budget += project.budget
        total_used += project.funds_used

    if total_used > total_budget:
        gross_percent = (total_used - total_budget) / total_budget * 100
        predominant_status = f"Exceeded"

    elif total_used < total_budget:
        gross_percent = total_used / total_budget * 100
        predominant_status = f"Used"

    else:
        gross_percent = 100.00
        predominant_status = "Fully utilized"

    return predominant_status, gross_percent


def budget_status_uncompleted(projects: List[Project]) -> Union[Tuple[str, float], Tuple[str, bool]]:
    if not projects:
        return "There are no uncompleted projects", False

    total_budget = 0
    total_used = 0

    for project in projects:
        total_budget += project.budget
        total_used += project.funds_used

    if total_used > total_budget:
        gross_percent = (total_used - total_budget) / total_budget * 100
        predominant_status = f"Exceeded"

    elif total_used < total_budget:
        gross_percent = total_used / total_budget * 100
        predominant_status = f"Used"

    else:
        gross_percent = 100.00
        predominant_status = "Fully utilized"

    return predominant_status, gross_percent
