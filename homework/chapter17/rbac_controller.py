import uvicorn
from enum import Enum
from typing import List, Optional, Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# 1. 定义权限枚举
class Permission(str, Enum):
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    DELETE_USERS = "delete_users"
    READ_PRODUCTS = "read_products"
    WRITE_PRODUCTS = "write_products"
    ACCESS_DEV_TOOLS = "access_dev_tools"
    VIEW_LOGS = "view_logs"

# 2. 定义角色枚举
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    DEVELOPER = "developer"

# 3. 定义角色与权限的映射
ROLE_PERMISSIONS_MAP: Dict[Role, List[Permission]] = {
    Role.ADMIN: [
        Permission.READ_USERS, Permission.WRITE_USERS, Permission.DELETE_USERS,
        Permission.READ_PRODUCTS, Permission.WRITE_PRODUCTS,
        Permission.ACCESS_DEV_TOOLS, Permission.VIEW_LOGS
    ],
    Role.USER: [
        Permission.READ_PRODUCTS, Permission.WRITE_PRODUCTS
    ],
    Role.GUEST: [
        Permission.READ_PRODUCTS
    ],
    Role.DEVELOPER: [
        Permission.READ_USERS, Permission.READ_PRODUCTS,
        Permission.ACCESS_DEV_TOOLS, Permission.VIEW_LOGS
    ]
}

# 4. 定义用户模型 (包含权限)
class User(BaseModel):
    username: str
    password: str # 实际应用中不应该直接存储密码，这里仅为模拟
    role: Role
    permissions: List[Permission] = [] # 运行时根据角色填充

# 5. 登录请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 模拟用户数据库
MOCK_USERS_DB: Dict[str, User] = {
    "admin_user": User(username="admin_user", password="admin_password", role=Role.ADMIN),
    "normal_user": User(username="normal_user", password="user_password", role=Role.USER),
    "guest_user": User(username="guest_user", password="guest_password", role=Role.GUEST),
    "developer_user": User(username="developer_user", password="dev_password", role=Role.DEVELOPER),
}

# 模拟 OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # tokenUrl 指向登录接口

# 模拟认证函数
def authenticate_user(username: str, password: str) -> Optional[User]:
    user = MOCK_USERS_DB.get(username)
    if not user or user.password != password:
        return None
    
    # 根据角色填充权限
    user.permissions = ROLE_PERMISSIONS_MAP.get(user.role, [])
    return user

# 模拟创建访问令牌
def create_access_token(user: User) -> str:
    # 实际应用中会生成 JWT，这里简化为用户名
    return user.username

# 6. 获取当前用户的依赖 (从令牌中解析并获取权限)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # 实际应用中会验证 JWT 令牌并解码
    # 这里简单地将 token 视为用户名
    username = token
    user = MOCK_USERS_DB.get(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 填充用户的权限
    user.permissions = ROLE_PERMISSIONS_MAP.get(user.role, [])
    return user

# 7. RBAC 权限控制装饰器 (支持角色和权限)
def rbac_required(
    allowed_roles: Optional[List[Role]] = None,
    required_permissions: Optional[List[Permission]] = None
):
    """
    一个基于角色和权限的访问控制装饰器。
    - allowed_roles: 允许访问的角色列表。
    - required_permissions: 访问所需的权限列表 (用户必须拥有所有这些权限)。
    """
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            # 检查角色
            if allowed_roles:
                if current_user.role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied. Required roles: {[role.value for role in allowed_roles]}",
                    )
            
            # 检查权限
            if required_permissions:
                # 检查用户是否拥有所有必需的权限
                if not all(p in current_user.permissions for p in required_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied. Required permissions: {[p.value for p in required_permissions]}",
                    )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

app = FastAPI(
    title="RBAC Demo API with Login and Permissions",
    description="A FastAPI application demonstrating Role-Based Access Control with user login and granular permissions.",
    version="1.0.0",
)

@app.post("/token", summary="模拟用户登录并获取访问令牌")
async def login_for_access_token(form_data: LoginRequest):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", summary="公共接口")
async def read_root():
    return {"message": "Welcome to the RBAC Demo API!"}

@app.get("/admin_dashboard", summary="管理员仪表盘 (仅限管理员角色)")
@rbac_required(allowed_roles=[Role.ADMIN])
async def admin_dashboard(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, Admin {current_user.username}! Welcome to the admin dashboard."}

@app.get("/user_profile", summary="用户个人资料 (用户和管理员角色)")
@rbac_required(allowed_roles=[Role.USER, Role.ADMIN])
async def user_profile(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! This is your profile."}

@app.get("/products", summary="查看产品列表 (所有认证用户)")
@rbac_required(allowed_roles=[Role.ADMIN, Role.USER, Role.GUEST, Role.DEVELOPER])
async def get_products(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! Here are the products."}

@app.post("/products", summary="创建产品 (需要 write_products 权限)")
@rbac_required(required_permissions=[Permission.WRITE_PRODUCTS])
async def create_product(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! You can create products."}

@app.get("/dev_tools", summary="开发工具 (需要 access_dev_tools 权限)")
@rbac_required(required_permissions=[Permission.ACCESS_DEV_TOOLS])
async def dev_tools(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! Accessing developer tools."}

@app.get("/system_logs", summary="查看系统日志 (需要 view_logs 权限)")
@rbac_required(required_permissions=[Permission.VIEW_LOGS])
async def system_logs(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! Viewing system logs."}

@app.delete("/delete_user/{username}", summary="删除用户 (需要 delete_users 权限)")
@rbac_required(required_permissions=[Permission.DELETE_USERS])
async def delete_user_endpoint(username: str, current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! Deleting user {username}."}

# 运行应用
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
