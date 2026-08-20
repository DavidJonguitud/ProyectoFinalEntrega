class ProjectException(Exception):
    pass


class ProjectNotFoundError(ProjectException):
    def __init__(self, project_id: int):
        super().__init__(f"Project with ID {project_id} does not exist.")


class ProjectAlreadyExistsError(ProjectException):
    def __init__(self, name: str):
        super().__init__(f"A project with name '{name}' already exists.")


class UnauthorizedAccessException(ProjectException):
    def __init__(self, project_id: int, user_email: str):
        super().__init__(
            f"User '{user_email}' does not have access to project {project_id}."
        )
