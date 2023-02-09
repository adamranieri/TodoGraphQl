import strawberry
from random import randint
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Generic, List, TypeVar
T = TypeVar("T")

@strawberry.type
class Todo:
    todoId: int 
    title: str 
    desc: str 
    isComplete: bool


@strawberry.type
class DeletionInformation:
    message:str


@strawberry.input
class TodoInput:
    todoId: int    
    title: str    
    desc: str    
    isComplete: bool


@strawberry.input
class UpdateTodosInput:
    updatedTodos: list[TodoInput]



todos:list[Todo] = []

# query resolver
def todo_resolver(title:str | None = None) -> list[Todo]:

    if title:
        return [t for t in todos if title in t.title]
    
    return todos
    
#mutations
def update_todos(input: UpdateTodosInput) -> list[Todo]:  
    global todos
    todos = [Todo(**t.__dict__) for t in input.updatedTodos]
    return todos


def clear_todos() ->DeletionInformation:
    size = len(todos)
    todos.clear()
    return DeletionInformation(message=f'{size} todos deleted')


@strawberry.type
class Query:
    todos: list[Todo] = strawberry.field(resolver=todo_resolver)


@strawberry.type
class Mutation:
    update_todos: list[Todo] = strawberry.field(resolver=update_todos)
    clear_todos: DeletionInformation = strawberry.field(resolver=clear_todos)

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(graphql_app, prefix="/graphql")