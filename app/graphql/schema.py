from ariadne import QueryType, MutationType, make_executable_schema, format_error, graphql_sync
from ariadne.asgi import GraphQL
from fastapi import FastAPI

from app.graphql.resolvers import resolve_hello, resolve_get_users, resolve_create_user

from app.metrics.prometheus_metrics import GQL_ERRORS
from app.metrics.qos_monitor import qos_monitor

# from starlette.responses import JSONResponse
# import traceback

# Định nghĩa GraphQL schema
type_defs = """
type Query {
    hello: String!
    getUsers: [User!]!
}

type Mutation {
    createUser(name: String!, email: String!): User!
}

type User {
    id: ID!
    name: String!
    email: String!
}
"""

def setup_graphql(app: FastAPI):
    """
    Cài đặt GraphQL cho ứng dụng FastAPI
    """
    # Khởi tạo Query type
    query = QueryType()
    query.set_field("hello", resolve_hello)
    query.set_field("getUsers", resolve_get_users)
    
    # Khởi tạo Mutation type
    mutation = MutationType()
    mutation.set_field("createUser", resolve_create_user)
    
    # Tạo schema
    schema = make_executable_schema(type_defs, query, mutation)
    
    # Tích hợp GraphQL vào FastAPI
    graphql_app = GraphQL(schema, debug=True)
    #graphql_app = GraphQL(schema, debug=True, error_formatter=custom_format_error)

    #app.add_middleware(GraphQLExceptionCatcher)
    
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)
    
    return schema
