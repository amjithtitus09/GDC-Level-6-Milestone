from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from .views import TaskListView
User = get_user_model()

class QuestionModelTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="bruce_wayne", email="bruce@gotham.org", password="i_am_batman")


    def test_authenticated(self):

        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        print(response)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    def test_authenticated(self):

        request = self.factory.get("/tasks/")
        request.user = self.user
        self.assertEqual(TaskListView.as_view()(request).status_code, 200)
