from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_access import ProjectRole
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.project_access import ProjectAccessRepository
from app.schemas.project import ProjectCreate
from app.schemas.project_access import ProjectAccessCreate
from app.services.project import ProjectService

pytestmark = pytest.mark.asyncio

# async def test_service_create_project_success(client: AsyncClient, auth_headers: dict): #No se deberia usar el client
#     project_payload = {
#         "name":"Proyecto de Prueba Automatizado",
#         "description":"Esto es una prueba"
#     }

#     mocked_proyect = Project(
#         id=99,
#         name=project_payload["name"],
#         description=project_payload["description"]
#     )

#     mocked_service = MagicMock(spec=ProjectService)

#     async def mock_create_project(*arg, **kwargs):
#         return mocked_proyect

#     mocked_service.create_project = mock_create_project

#     from app.main import app
#     app.dependency_overrides[get_project_service] = lambda: mocked_service

#     response = await client.post("/projects", json=project_payload, headers=auth_headers)

#     app.dependency_overrides.clear()

#     data = response.json()

#     assert response.status_code == 200

#     assert data["id"] == 99
#     assert data["name"] == project_payload["name"]
#     assert data["description"] == project_payload["description"]


# Crear instancia de project service
# Comprobar la ló


async def test_service_create_project_success():
    test_user = User(
        id=1,
        email="bla@bla.com",
    )

    mock_db_project = MagicMock(spec=Session)
    mock_repo_project = MagicMock(spec=ProjectRepository)
    mock_access_repo_project = MagicMock(sepc=ProjectAccessRepository)

    service = ProjectService(
        db=mock_db_project,
        project_repo=mock_repo_project,
        project_access_repo=mock_access_repo_project,
    )

    project_payload = ProjectCreate(name="project test", description="testing project")

    mocked_project = Project(
        id=12, name=project_payload.name, description=project_payload.description
    )

    service.project_repo.get_project_by_name.return_value = None

    service.project_repo.create_project.return_value = mocked_project

    result = await service.create_project(project_data=project_payload, owner=test_user)

    assert result.id == 12
    assert result.name == "project test"

    mock_repo_project.get_project_by_name.assert_called_once_with("project test")
    mock_repo_project.create_project.assert_called_once_with(project_payload)

    mock_access_repo_project.create_project_access.assert_called_once()
    called_args, _ = mock_access_repo_project.create_project_access.call_args
    access_arg = called_args[0]

    assert isinstance(access_arg, ProjectAccessCreate)
    assert access_arg.project_id == 12
    assert access_arg.email == test_user.email
    assert access_arg.role == ProjectRole.OWNER

    mock_db_project.flush.assert_called_once()
    mock_db_project.commit.assert_called_once()
    mock_db_project.refresh.assert_called_once()
    mock_db_project.rollback.assert_not_called()


async def test_service_create_project_already_exists():

    # ARRANGE
    # Inicializamos mocks y dependencias de la prueba
    test_user = User(
        id=1,
        email="bla@bla.com",
    )
    mock_db_project = MagicMock(spec=Session)
    mock_repo_project = MagicMock(spec=ProjectRepository)
    mock_access_repo_project = MagicMock(sepc=ProjectAccessRepository)

    service = ProjectService(
        db=mock_db_project,
        project_repo=mock_repo_project,
        project_access_repo=mock_access_repo_project,
    )

    project_payload = ProjectCreate(name="project test", description="testing project")

    existing_project = Project(id=12, name="test service", description="it exists")

    # Act
    # Ejecutamos el metodo que estamos probando
    service.project_repo.get_project_by_name.return_value = existing_project

    with pytest.raises(ValueError) as exc_info:
        await service.create_project(project_payload, test_user)

    # Assert
    # Verificamos que el retorno del servicio sea el que esperamos
    assert str(exc_info.value) == "A project with that name already exists"

    mock_repo_project.create_project.assert_not_called()
    mock_access_repo_project.create_project_access.assert_not_called()
    mock_db_project.commit.assert_not_called()
