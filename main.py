import strawberry
from random import randint
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@strawberry.type
class Todo:
    todoId: int 
    title: str 
    desc: str 
    isComplete: bool

@strawberry.type
class TodoDoesNotExist:
    todoId: int 
    message: str

@strawberry.type
class DeletionInformation:
    message:str

@strawberry.input
class TodoIdentificationInput:
    todoId: int

@strawberry.input
class TodoCreationInput:
    title: str 
    desc: str 



Response = strawberry.union(
    "AddStatsResponse", [Todo, TodoDoesNotExist]
)

todos:dict[int, Todo] = {}

# query resolver
def todo_resolver(title:str | None = None) -> list[Todo]:

    if title:
        return [t for t in list(todos.values()) if title in t.title]
    
    return list(todos.values())
    
# mutations
def create_todo(input: TodoCreationInput) -> Todo:  
    todo = Todo(todoId=randint(100,999), title=input.title, desc=input.desc, isComplete=False)
    todos[todo.todoId] = todo
    return todo

def complete_todo(input: TodoIdentificationInput) -> Response:  # type: ignore
    
    if todo := todos.get(input.todoId):
        todo.isComplete = True
        return todo
    
    return TodoDoesNotExist(todoId=input.todoId, message="todo does not exist")

def clear_todos() ->DeletionInformation:
    size = len(todos)
    todos.clear()
    return DeletionInformation(message=f'{size} todos deleted')


@strawberry.type
class Query:
    todos: list[Todo] = strawberry.field(resolver=todo_resolver)


@strawberry.type
class Mutation:
    create_todo: Todo = strawberry.field(resolver=create_todo)
    complete_todo: Todo | TodoDoesNotExist = strawberry.field(resolver=complete_todo)
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