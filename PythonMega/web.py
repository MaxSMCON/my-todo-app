import streamlit as st
import functions

def add_todo():
    todo = st.session_state['new_todo']
    todos.append(todo)
    functions.write_todos(todos)


todos = functions.get_todos()

st.title("My Todo App")
st.subheader("This is my to do file")
st.write("This app to increase your productivity")

for index, todo in enumerate(todos):
    st.checkbox(todo, key=f"checkbox_{index}")

st.text_input(label="", placeholder="Add new todo...",
              on_change= add_todo, key='new_todo')

print('Hello')

st.session_state