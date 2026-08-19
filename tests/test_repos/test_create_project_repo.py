import pytest
from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate

def test_repo_create_project_success(db_session: Session):
    #Arrange
    #Configuramos los mocks y variables que utilizaremos en el set
    repo = ProjectRepository(db_session)

    project_data = ProjectCreate(
        name="Proyecto repo test",
        description="Verificando persistencia directa en SQLAlchemy"
    )

    #Act
    #Ejecutamos los metodos a probar
    
    saved_project = repo.create_project(project_data)

    #Arrange
    #Comprobamos que el comportamiento sea el esperado

    assert saved_project.id is not None
    assert saved_project.name == "Proyecto repo test"
    assert saved_project.description == "Verificando persistencia directa en SQLAlchemy"

    db_project = db_session.query(Project).filter(Project.id == saved_project.id).first()
    assert db_project is not None
    assert db_project.name == "Proyecto repo test"

def test_repo_get_project_by_id_found(db_session: Session):
    #Arrange
    #Configuramos los mocks y variables que utilizaremos en el set
    existing_project = Project(
        name="Proyecto Existente",
        description="Guardado directamente para busqueda"
    )
    db_session.add(existing_project)
    db_session.flush()

    #Act
    #Ejecutamos los metodos a probar
    repo = ProjectRepository(db_session)

    found_project = repo.get_project_by_id(existing_project.id)


    #Arrange
    #Comprobamos que el comportamiento sea el esperado
    assert found_project is not None
    assert found_project.id == existing_project.id
    assert found_project.name == "Proyecto Existente"

def test_repo_get_project_by_id_not_found(db_session: Session):
    repo = ProjectRepository(db_session)

    found_project = repo.get_project_by_id(9999)

    assert found_project is None