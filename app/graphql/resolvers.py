from app.graphql.decorators import gql_metrics_decorator
import asyncio

@gql_metrics_decorator
async def resolve_hello(_, info):
    """
    Resolver đơn giản trả về "Hello, world!"
    """
    return "Hello, world!"

@gql_metrics_decorator
async def resolve_get_users(_, info):
    """
    Resolver lấy danh sách users (giả lập)
    """
    # Giả lập một độ trễ khi truy vấn database
    await asyncio.sleep(0.1)
    
    return [
        {"id": "1", "name": "User 1", "email": "user1@example.com"},
        {"id": "2", "name": "User 2", "email": "user2@example.com"}
    ]

@gql_metrics_decorator
async def resolve_create_user(_, info, name, email):
    """
    Resolver tạo user mới (giả lập)
    """
    # Giả lập một độ trễ khi tạo dữ liệu
    await asyncio.sleep(0.2)
    
    # Giả lập tạo user
    return {"id": "3", "name": name, "email": email}

# Ví dụ về một GraphQL container với decorator
from app.graphql.decorators import monitor_gql_container

@monitor_gql_container
class UserContainer:
    async def resolve_user(self, info, id):
        """
        Lấy thông tin chi tiết về user
        """
        # Giả lập truy vấn database
        await asyncio.sleep(0.1)
        return {"id": id, "name": f"User {id}", "email": f"user{id}@example.com"}