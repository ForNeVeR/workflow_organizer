from django.test import TestCase
from assignment_handler.helper import calculate_average_progress, budget_status_completed, budget_status_uncompleted
from assignment_handler.models import Project


class AssignmentHandlerHelperTestCase(TestCase):
    def test_calculate_average_progress_empty_list(self):
        projects = []

        self.assertEqual(calculate_average_progress(projects), 0.00)

    def test_calculate_average_progress_single_project(self):
        project = Project()
        project.get_project_progress = lambda: 50
        projects = [project]

        self.assertEqual(calculate_average_progress(projects), 50.00)

    def test_calculate_average_progress_multiple_project(self):
        project1 = Project()
        project2 = Project()
        project3 = Project()
        project1.get_project_progress = lambda: 10
        project2.get_project_progress = lambda: 20
        project3.get_project_progress = lambda: 30
        projects = [project1, project2, project3]

        self.assertEqual(calculate_average_progress(projects), 20.00)

    def test_budget_status_completed_no_projects(self):
        projects = []
        status, percent = budget_status_completed(projects)

        self.assertEqual(status, "There are no completed projects")
        self.assertFalse(percent)

    def test_budget_status_completed_under_budget(self):
        project1 = Project(budget=100, funds_used=80)
        project2 = Project(budget=200, funds_used=150)
        projects = [project1, project2]

        status, percent = budget_status_completed(projects)

        self.assertEqual(status, "Used")
        self.assertAlmostEqual(percent, 76.66666666666667)

    def test_budget_status_completed_over_budget(self):
        project1 = Project(budget=100, funds_used=150)
        projects = [project1]

        status, percent = budget_status_completed(projects)

        self.assertEqual(status, "Exceeded")
        self.assertEqual(percent, 50.00)

    def test_budget_status_completed_on_budget(self):
        project1 = Project(budget=100, funds_used=100)
        projects = [project1]

        status, percent = budget_status_completed(projects)

        self.assertEqual(status, "Fully utilized")
        self.assertEqual(percent, 100.00)

    def test_budget_status_uncompleted_no_projects(self):
        projects = []
        status, percent = budget_status_uncompleted(projects)

        self.assertEqual(status, "There are no uncompleted projects")
        self.assertFalse(percent)

    def test_budget_status_uncompleted_under_budget(self):
        project1 = Project(budget=100, funds_used=80)
        project2 = Project(budget=200, funds_used=100)
        projects = [project1, project2]

        status, percent = budget_status_uncompleted(projects)

        self.assertEqual(status, "Used")
        self.assertEqual(percent, 60.00)

    def test_budget_status_uncompleted_over_budget(self):
        project1 = Project(budget=100, funds_used=150)
        projects = [project1]

        status, percent = budget_status_uncompleted(projects)

        self.assertEqual(status, "Exceeded")
        self.assertEqual(percent, 50.00)

    def test_budget_status_uncompleted_on_budget(self):
        project1 = Project(budget=100, funds_used=50)
        project2 = Project(budget=100, funds_used=60)
        projects = [project1, project2]

        status, percent = budget_status_uncompleted(projects)

        self.assertEqual(status, "Used")
        self.assertAlmostEqual(percent, 55.00000000000001)
