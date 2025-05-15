
class DeleteError(Exception):
    pass

class AlreadyExistsError(Exception):
    def __init__(self, entity_name: str, value: str):
        super().__init__(f"{entity_name} '{value}' ya existe.")

class ChangeAdminRoleError(Exception):
    pass

class EmptyFieldError(Exception):
    pass

class LoginError(Exception):
    pass

class NotFoundError(Exception):
    def __init__(self, entity_name: str, entity_id: int):
        super().__init__(f"{entity_name} con ID {entity_id} no encontrado.")
