import unittest
import docker
from .. import helpers


class ServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        client = docker.from_env()
        helpers.force_leave_swarm(client)
        client.swarm.init()

    @classmethod
    def tearDownClass(cls):
        helpers.force_leave_swarm(docker.from_env())

    def test_create(self):
        client = docker.from_env()
        name = helpers.random_name()
        service = client.services.create(
            # create arguments
            name=name,
            labels={'foo': 'bar'},
            # ContainerSpec arguments
            image="alpine",
            command="sleep 300",
            container_labels={'container': 'label'}
        )
        assert service.name == name
        assert service.attrs['Spec']['Labels']['foo'] == 'bar'
        container_spec = service.attrs['Spec']['TaskTemplate']['ContainerSpec']
        assert container_spec['Image'] == "alpine"
        assert container_spec['Labels'] == {'container': 'label'}

    def test_get(self):
        client = docker.from_env()
        name = helpers.random_name()
        service = client.services.create(
            name=name,
            image="alpine",
            command="sleep 300"
        )
        service = client.services.get(service.id)
        assert service.name == name

    def test_list_remove(self):
        client = docker.from_env()
        service = client.services.create(
            name=helpers.random_name(),
            image="alpine",
            command="sleep 300"
        )
        assert service in client.services.list()
        service.remove()
        assert service not in client.services.list()

    def test_tasks(self):
        client = docker.from_env()
        service1 = client.services.create(
            name=helpers.random_name(),
            image="alpine",
            command="sleep 300"
        )
        service2 = client.services.create(
            name=helpers.random_name(),
            image="alpine",
            command="sleep 300"
        )
        tasks = []
        while len(tasks) == 0:
            tasks = service1.tasks()
        assert len(tasks) == 1
        assert tasks[0]['ServiceID'] == service1.id

        tasks = []
        while len(tasks) == 0:
            tasks = service2.tasks()
        assert len(tasks) == 1
        assert tasks[0]['ServiceID'] == service2.id

    def test_update(self):
        client = docker.from_env()
        service = client.services.create(
            # create arguments
            name=helpers.random_name(),
            # ContainerSpec arguments
            image="alpine",
            command="sleep 300"
        )
        new_name = helpers.random_name()
        service.update(
            # create argument
            name=new_name,
            # ContainerSpec argument
            command="sleep 600"
        )
        service.reload()
        assert service.name == new_name
        container_spec = service.attrs['Spec']['TaskTemplate']['ContainerSpec']
        assert container_spec['Command'] == ["sleep", "600"]
