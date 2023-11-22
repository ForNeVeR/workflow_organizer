from unittest import mock

from django.forms import model_to_dict
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from assignment_handler import views
from assignment_handler.models import Worker, Task, TaskType, Project, ProjectCategory, Team


class AssignmentHandlerViewsTestCase(TestCase):

    fixtures = ["fixtures/fixture_test_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.initial_num_workers = Worker.objects.count()
        cls.initial_num_tasks = Task.objects.count()
        cls.initial_num_projects = Project.objects.count()

    def test_worker_detail_get(self):
        url = f"/workers/{2}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/accounts/login/?next={url}")

    def test_worker_detail_post(self):
        url = f"/workers/{2}/"

        data = {'score': 5}

        evaluator = Worker.objects.get(id=1)
        worker = Worker.objects.get(id=2)

        self.client.force_login(evaluator)

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/workers/{2}/")

        worker.rating_points += 5

        self.assertEqual(worker.rating_points, 8)

    def test_worker_create_post_valid(self):
        worker = Worker.objects.get(id=2)

        new_worker = Worker()
        new_worker.id = Worker.objects.latest("id").id + 1
        new_worker.save()

        worker_dict = model_to_dict(worker)
        worker_dict["position"] = worker.position

        for field in worker_dict:
            if hasattr(new_worker, field):
                if field == "groups" or field == "user_permissions" or field == "teams":
                    getattr(new_worker, field).set(getattr(worker, field).all())
                else:
                    setattr(new_worker, field, worker_dict[field])

        new_worker.save()

        response = self.client.post("/register/", worker_dict)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Worker.objects.count(), self.initial_num_workers + 1)

    def test_worker_update_post_valid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        worker1 = Worker.objects.get(id=2)
        worker2 = Worker.objects.get(id=3)

        workers = [worker1, worker2]

        updated_data = {
            "first_name": "Updated name",
            "email": "new@email.com"
        }

        for worker in workers:
            for field, value in updated_data.items():
                setattr(worker, field, value)

        for worker in workers:
            worker.save()

        url = reverse("assignment_handler:worker-update", args=[worker.id])
        response = self.client.post(url, updated_data)

        self.assertEqual(response.status_code, 200)

        for worker in workers:
            self.assertEqual(worker.first_name, updated_data["first_name"])
            self.assertEqual(worker.email, updated_data["email"])

    def test_worker_update_post_invalid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        worker1 = Worker.objects.get(id=2)
        worker2 = Worker.objects.get(id=3)

        workers = [worker1, worker2]

        updated_data = {
            "first_name": "Updated name",
            "email": "new@email.com"
        }

        for worker in workers:
            for field, value in updated_data.items():
                setattr(worker, field, value)

        for worker in workers:
            worker.save()

        url = reverse("assignment_handler:worker-update", args=[worker.id])
        response = self.client.post(url, updated_data)

        self.assertEqual(response.status_code, 200)

        for worker in workers:
            self.assertEqual(worker.first_name, updated_data["first_name"])
            self.assertEqual(worker.email, updated_data["email"])

    def test_task_create_post_valid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        url = reverse("assignment_handler:task-create")

        task = Task.objects.get(id=15)

        new_task = Task()
        new_task.id = Task.objects.latest("id").id + 1
        new_task.time_constraints = task.time_constraints
        new_task.task_type_id = task.task_type_id
        new_task.save()

        task_dict = model_to_dict(task)
        task_dict["task_type"] = task.task_type

        for field in task_dict:
            if hasattr(new_task, field):
                if field == "assignees":
                    getattr(new_task, field).set(getattr(task, field).all())
                else:
                    setattr(new_task, field, task_dict[field])

        new_task.save()

        response = self.client.post(url, {"task": new_task.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), self.initial_num_tasks + 1)

    def test_task_create_post_invalid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        task_type_instance = TaskType.objects.get(id=1)

        new_task = Task(
            name="Initial name",
            depiction="Task for test purposes",
            time_constraints='2024-01-01',
            task_type=task_type_instance
        )

        new_task.full_clean()
        new_task.save()

        new_task.name = ""
        new_task.full_clean(exclude=["name", "depiction", "time_constraints", "task_type"])

        new_task.save()

        url = reverse("assignment_handler:task-create")
        response = self.client.post(url, {"task": new_task.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), self.initial_num_tasks + 1)

        new_task = Task.objects.latest("id")

        self.assertNotEqual(new_task.name, "Initial name")
        self.assertEqual(new_task.task_type, task_type_instance)

    def test_task_update_post_valid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        task1 = Task.objects.get(id=15)
        task2 = Task.objects.get(id=21)
        task3 = Task.objects.get(id=22)

        tasks = [task1, task2, task3]

        updated_data = {
            "name": "Updated name",
            "priority": "S"
        }

        for task in tasks:
            for field, value in updated_data.items():
                setattr(task, field, value)

        for task in tasks:
            task.save()

        url = reverse("assignment_handler:task-update", args=[task.id])
        response = self.client.post(url, {"task": task.id})

        self.assertEqual(response.status_code, 200)

        for task in tasks:
            self.assertEqual(task.name, updated_data["name"])
            self.assertEqual(task.priority, updated_data["priority"])

    def test_task_update_post_invalid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        task1 = Task.objects.get(id=15)
        task2 = Task.objects.get(id=21)

        original_name1, original_priority1 = task1.name, task1.priority
        original_name2, original_priority2 = task2.name, task2.priority

        updated_data = {
            "name": "Updated name",
            "priority": "S"
        }

        for task in [task1, task2]:
            for field, value in updated_data.items():
                setattr(task, field, value)

        for task in [task1, task2]:
            task.save()

        url = reverse("assignment_handler:task-update", args=[task.id])
        response = self.client.post(url, {"task": task.id})

        self.assertEqual(response.status_code, 200)

        updated_task1 = Task.objects.get(id=task1.id)
        updated_task2 = Task.objects.get(id=task2.id)

        self.assertNotEqual(
            (updated_task1.name, updated_task1.priority),
            (original_name1, original_priority1)
        )

        self.assertNotEqual(
            (updated_task2.name, updated_task2.priority),
            (original_name2, original_priority2)
        )

    @mock.patch("assignment_handler.views.ProjectCreate.as_view")
    def test_project_create_post_valid(self, mock_view):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        mock_view.return_value = HttpResponse(status=302)

        project = Project.objects.get(id=5)

        new_project = Project.objects.create(
            name="Test project",
            depiction="Project for test purposes",
            **{field.name: getattr(project, field.name) for field in Project._meta.fields if
               field.name not in ["id", "name", "depiction"]}
        )

        new_project.save()

        project_dict = model_to_dict(project)
        project_dict["project_category"] = project.project_category
        project_dict["team"] = project.team

        for field in project_dict:
            if hasattr(new_project, field):
                if field == "teams":
                    getattr(new_project, field).set(getattr(project, field).all())

        new_project.save()

        response = views.ProjectCreate.as_view()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), self.initial_num_projects + 1)

    def test_project_create_post_invalid(self):
        project_category_instance = ProjectCategory.objects.get(id=1)

        new_project = Project(
            name="Test project",
            depiction="Project for test purposes",
            time_constraints="2024-01-01",
            project_category=project_category_instance
        )

        new_project.full_clean()
        new_project.save()

        new_project.name = ""
        new_project.full_clean(exclude=["name", "depiction", "time_constraints", "project_category"])

        new_project.save()

        url = reverse("assignment_handler:project-create")
        response = self.client.post(url, {"project": new_project.id})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), self.initial_num_projects + 1)

        new_project = Project.objects.latest("id")

        self.assertNotEqual(new_project.name, "Valid name")
        self.assertEqual(new_project.project_category, project_category_instance)

    def test_project_update_post_valid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        project1 = Project.objects.get(id=5)
        project2 = Project.objects.get(id=6)
        project3 = Project.objects.get(id=7)

        projects = [project1, project2, project3]

        updated_data = {
            "name": "Updated name",
            "priority": "S"
        }

        for project in projects:
            for field, value in updated_data.items():
                setattr(project, field, value)

        for project in projects:
            project.save()

        url = reverse("assignment_handler:task-update", args=[project.id])
        response = self.client.post(url, {"task": project.id})

        self.assertEqual(response.status_code, 404)

        for project in projects:
            self.assertEqual(project.name, updated_data['name'])
            self.assertEqual(project.priority, updated_data['priority'])

    def test_project_update_post_invalid(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        project1 = Project.objects.get(id=5)
        project2 = Project.objects.get(id=6)

        original_name1, original_priority1 = project1.name, project1.priority
        original_name2, original_priority2 = project2.name, project2.priority

        updated_data = {
            "name": "Updated name",
            "priority": "S"
        }

        for project in [project1, project2]:
            for field, value in updated_data.items():
                setattr(project, field, value)

        for project in [project1, project2]:
            project.save()

        url = reverse("assignment_handler:task-update", args=[project.id])
        response = self.client.post(url, {"task": project.id})

        self.assertEqual(response.status_code, 404)

        updated_project1 = Project.objects.get(id=project1.id)
        updated_project2 = Project.objects.get(id=project2.id)

        self.assertNotEqual(
            (updated_project1.name, updated_project1.priority),
            (original_name1, original_priority1)
        )

        self.assertNotEqual(
            (updated_project2.name, updated_project2.priority),
            (original_name2, original_priority2)
        )

    def test_toggle_assign_task_unassigned(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        task = Task.objects.get(id=15)

        self.assertNotIn(user, task.assignees.all())

        task.assignees.add(user)

        self.assertIn(user, task.assignees.all())

        url = reverse("assignment_handler:toggle-task-assign", args=[task.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_toggle_assign_task_assigned(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        task = Task.objects.get(id=21)

        self.assertIn(user, task.assignees.all())

        task.assignees.remove(user)

        self.assertNotIn(user, task.assignees.all())

        url = reverse("assignment_handler:toggle-task-assign", args=[task.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_toggle_team_is_not_member(self):
        workers = [
            Worker.objects.get(id=2),
            Worker.objects.get(id=3)
        ]

        teams = [
            Team.objects.get(id=1),
            Team.objects.get(id=2),
            Team.objects.get(id=3)
        ]

        for team in teams:
            for worker in workers:
                if worker not in team.members.all():
                    team.members.add(worker)
                    team.save()

                    url = reverse("assignment_handler:toggle-team-transition", args=[worker.pk, team.pk])
                    response = self.client.get(url)

                    self.assertEqual(response.status_code, 302)
                    self.assertIn(worker, team.members.all())

    def test_toggle_team_is_member(self):
        workers = [
            Worker.objects.get(id=2),
            Worker.objects.get(id=3)
        ]

        teams = [
            Team.objects.get(id=1),
            Team.objects.get(id=2),
            Team.objects.get(id=3)
        ]

        for team in teams:
            for worker in workers:
                if worker in team.members.all():
                    team.members.remove(worker)
                    team.save()

                    url = reverse("assignment_handler:toggle-team-transition", args=[worker.pk, team.pk])
                    response = self.client.get(url)

                    self.assertEqual(response.status_code, 302)
                    self.assertNotIn(worker, team.members.all())

    def test_switch_team_add(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        team = Team.objects.get(id=3)

        team.members.add(user)

        url = reverse("assignment_handler:switch-team", args=[team.id, "add"])
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(team.members.filter(username="marshall").exists())

    def test_switch_team_remove(self):
        user = Worker.objects.get(id=1)

        self.client.force_login(user)

        team = Team.objects.get(id=3)

        team.members.remove(user)

        url = reverse("assignment_handler:switch-team", args=[team.id, "add"])
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(team.members.filter(username="marshall").exists())
