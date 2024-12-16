from Data.models import Task
# Operaciones CRUD
class TaskCRUD:
    def __init__(self, session):
        self.session = session

    def create_task(self, title, description, status):
        """Crea una nueva tarea."""
        task = Task(title=title, description=description, status=status)
        self.session.add(task)
        self.session.commit()
        return task

    def read_tasks(self):
        """Devuelve todas las tareas."""
        return self.session.query(Task).all()

    def find_tasks(self, title):
        task = self.session.query(Task).filter(Task.title == title).first()
        if not task:
            return False
        else:
            return True

    def update_task(self, task_id, title=None, description=None, status=None):
        """Actualiza una tarea existente."""
        task = self.session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        if title:
            task.title = title
        if description:
            task.description = description
        if status:
            task.status = status
        self.session.commit()
        return task

    def delete_task(self, task_id):
        """Elimina una tarea por su ID."""
        task = self.session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        self.session.delete(task)
        self.session.commit()
        return task

    def listTasksXStatus(self, status):
        tasks = self.session.query(Task).filter(Task.status == status)
        return tasks
    def listTaskXId(self, task_id):
        task = self.session.query(Task).filter(Task.id == task_id).first()
        return task