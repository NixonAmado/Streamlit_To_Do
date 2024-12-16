import streamlit as st
from streamlit import rerun, status
from streamlit_extras.stylable_container import stylable_container
from Data.database import init_db
from Data.models import Task
from sqlalchemy.orm import sessionmaker
from Styles.style import checkBoxStyle, floatDownloadBtn
from Data.endpoints import TaskCRUD
import json
from PIL import Image

# Inicialización de la base de datos y sesión
engine = init_db()
Session = sessionmaker(bind=engine)
session = Session()
background_url = "https://cdnpt01.viewbug.com/media/mediafiles/2015/11/12/60380221_medium.jpg"


st.set_page_config(page_title='TO DO✔️')

# Insertar CSS personalizado para cambiar el fondo
st.markdown(f"""
    <style>
        body {{
            background-image: url("{background_url}");
            background-size: cover;  /* Ajusta la imagen para cubrir toda la página */
            background-position: center;  /* Centra la imagen */
            background-attachment: fixed;  /* Hace que el fondo sea fijo mientras se desplaza */
        }}
    </style>
""", unsafe_allow_html=True)

# Estado inicial
if "crud" not in st.session_state:
    # Si no existe, crear la instancia de TaskCRUD
    st.session_state.crud = TaskCRUD(session)

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

if "show_sidebar_event" not in st.session_state:
    st.session_state.show_sidebar_event = False
    st.session_state.current_task_id = None
    st.session_state.taskTitle = None

def changeTaskPosition(task_id, action):
    st.session_state[f"checkbox_{task_id}"] = False
    if action == "toCompleted":
        st.session_state.crud.update_task(task_id,None,None,"Completed")
        return()
    if action == "toPending":
        st.session_state.crud.update_task(task_id,None,None,"Pending")
        return()

def showSideBar_Click(task_id=None, title=None):
    """Alternar el evento del sidebar."""
    if st.session_state.show_sidebar_event and st.session_state.current_task_id == task_id:
        # Si la barra está abierta para la misma tarea, se cierra
        st.session_state.show_sidebar_event = False
        st.session_state.current_task_id = None
    else:
        # Si la barra está cerrada o cambia la tarea seleccionada, se abre
        st.session_state.show_sidebar_event = True
        st.session_state.current_task_id =  task_id
        st.session_state.taskTitle = title

def pendingTasksList():
    """Renderiza la lista de tareas."""
    tasks = st.session_state.crud.listTasksXStatus("Pending")
    tasks_titles = [{"ID": task.id, "Title": task.title} for task in tasks]

    for task in tasks_titles:
        with stylable_container(key=f"TasksContainer_{task['ID']}", css_styles=checkBoxStyle):
            col1, col2 = st.columns([1, 11])

            with col1:
                st.checkbox("", key=f"checkbox_{task['ID']}", value=False, on_change=changeTaskPosition, args=(task['ID'], "toCompleted"))

            with col2:
                    st.button(task["Title"], on_click=showSideBar_Click, args=(task['ID'],task["Title"]))

def completedTasksList():
    """Renderiza la lista de tareas."""

    tasks = st.session_state.crud.listTasksXStatus("Completed")
    tasks_titles = [{"ID": task.id, "Title": task.title} for task in tasks]

    for task in tasks_titles:
        with stylable_container(key=f"TasksContainer_{task['ID']}", css_styles=checkBoxStyle):
            col1, col2 = st.columns([1, 11])

            with col1:
                st.checkbox("", key=f"checkbox_{task['ID']}", value=False,on_change=changeTaskPosition, args=(task['ID'], "toPending"))

            with col2:
                    st.button(task["Title"], on_click=showSideBar_Click, args=(task['ID'],))


if __name__ == "__main__":
    st.title("TO DO https://github.com/NixonAmado/Streamlit_To_Do")

    with st.expander("Tareas pendientes"):
        pendingTasksList()
    with st.expander("Tareas completadas"):
        completedTasksList()

    taskTitle = st.chat_input("Enter task title")
    if taskTitle:
        if st.session_state.crud.find_tasks(taskTitle):
            st.warning('This task name alredy exist', icon="⚠️")
        else:
            try:
                new_task = Task(title=taskTitle, status="Pending")
                session.add(new_task)
                session.commit()
                rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Error al guardar la tarea: {e}")

    uploaded_file = st.file_uploader("Sube un archivo JSON", type=["json"])
    if uploaded_file is not None:
        # Leer el contenido del archivo JSON
        data = json.load(uploaded_file)

        # Iterar sobre los datos JSON y agregar cada tarea a la base de datos
        for task_data in data:
            title = task_data.get("title")
            description = task_data.get("description")
            status = task_data.get("status")

            if title:
                # Crear una nueva tarea en la base de datos
                st.session_state.crud.create_task(title=title, description=description, status=status)

    tasks = st.session_state.crud.read_tasks()
    tasks_dict = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,  # Si tienes un campo 'status' en la tabla
        }
        tasks_dict.append(task_dict)

    # Convertir la lista de diccionarios en JSON
    json_data = json.dumps(tasks_dict, indent=4)
    # Botón para descargar el archivo JSON
    st.markdown(f"""
        <style>
        {floatDownloadBtn}
        </style>
    """, unsafe_allow_html=True)
    st.download_button(
        label="Download JSON",
        data=json_data,
        file_name="tasks.json",
        mime="application/json",
        key="download_json_button"
    )
    if st.session_state.show_sidebar_event:
        with st.sidebar:
            task_id = st.session_state.current_task_id
            task_description = st.session_state.user_input
            if task_id:
                task = st.session_state.crud.listTaskXId(task_id)
                task_bd_description = task.description or ""
            else:
                task_bd_description = ""
            st.markdown(f"<h3 style='text-align: center;'>Task {st.session_state.taskTitle}</h3>", unsafe_allow_html=True)
            st.session_state.user_input = st.text_area("Write a description", value=task_bd_description, height=200)

            if task_id:
                if st.button("Submit"):
                    try:
                        st.session_state.crud.update_task(task_id, None, task_description, None)
                        st.success('task succesfully updated')
                    except Exception as e:
                        session.rollback()
                        st.error(f"Error al actualizar la tarea: {e}")
                if st.button("Delete"):
                    try:
                        st.session_state.crud.delete_task(task_id)
                        st.success('task succesfully Deleted')
                        st.session_state.current_task_id = ""
                        st.session_state.taskTitle = ""
                        st.session_state.user_input = None
                        st.rerun()

                    except Exception as e:
                        session.rollback()
                        st.error(f"Error al eliminar la tarea: {e}")
                        st.rerun()
    else:
        st.sidebar.empty()
