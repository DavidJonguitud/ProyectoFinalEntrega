import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient
from app.main import app
from app.core.dependencies import get_project_service
from app.services.project import ProjectService
from app.schemas.project import ProjectResponse, ProjectCreate
from app.models.user import User


pytestmark = pytest.mark.asyncio

async def test_router_create_project_success(client: AsyncClient, auth_headers: dict, test_user: User):

    #Arrange
    #Configuramos los mocks que usaremos para las pruebas
    mock_service_response = {
        "id": 0,
        "name": "Proyecto mocked del router",
        "description": "logica del router aislada"
    }

    mock_service = MagicMock(spec=ProjectService)

    mock_service.create_project = AsyncMock(return_value=mock_service_response)

    app.dependency_overrides[get_project_service] = lambda: mock_service

    valid_payload = {
        "name":"Proyecto mockead del router",
        "description":"logica del router aislada"
    }

    #Act
    #Ejecutamos los metodos a probar
    response = await client.post("/projects", json=valid_payload, headers=auth_headers)

    app.dependency_overrides.clear()

    #Assert
    #Corroboramos que el comportamiento sea el esperado

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 0
    assert data["name"] == "Proyecto mocked del router"
    assert data["description"] == "logica del router aislada"

    mock_service.create_project.assert_called_once()
    mock_service.create_project.assert_called_with(ProjectCreate(**valid_payload), test_user)


async def test_router_create_project_validation_error(client: AsyncClient, auth_headers: dict):
    mock_service = MagicMock(spec=ProjectService)
    mock_service.create_project = AsyncMock()

    app.dependency_overrides[get_project_service] = lambda: mock_service

    invalid_payload = {
        "description": "Falta el nombre obligatorio"
    }

    response = await client.post("/projects", json=invalid_payload, headers=auth_headers)

    app.dependency_overrides.clear()

    assert response.status_code == 422

    mock_service.create_project.assert_not_called()
    