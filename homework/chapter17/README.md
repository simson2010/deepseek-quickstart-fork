# FastAPI RBAC 权限控制示例

这是一个使用 FastAPI 实现的基于角色 (Role-Based Access Control, RBAC) 和权限的 API 权限控制示例。它模拟了用户登录、获取访问令牌，并根据用户的角色和所拥有的权限来控制对不同 API 接口的访问。

## 功能特性

*   **角色定义**: 定义了管理员 (Admin)、普通用户 (User)、访客 (Guest) 和开发人员 (Developer) 等角色。
*   **权限定义**: 定义了细粒度的权限，例如 `read_users`、`write_products`、`access_dev_tools` 等。
*   **角色-权限映射**: 将不同的权限集合分配给不同的角色。
*   **用户认证模拟**: 模拟用户登录，通过用户名和密码获取访问令牌。
*   **访问令牌**: 模拟生成和使用访问令牌进行身份验证。
*   **RBAC 装饰器**: 一个灵活的装饰器，可以根据 `allowed_roles` (允许的角色) 和 `required_permissions` (必需的权限) 来保护 API 接口。
*   **FastAPI 集成**: 利用 FastAPI 的依赖注入系统，使权限控制逻辑与路由解耦。
*   **Swagger UI**: 自动生成交互式 API 文档，方便测试。

## 安装

在开始之前，请确保您的系统已安装 Python 3.7+。

1.  **克隆或下载项目**:
    如果您正在使用 Git，可以克隆此仓库：
    ```bash
    git clone <your-repo-url>
    cd RBAC_demo
    ```
    如果只是下载文件，请确保进入到包含 `rbac_controller.py` 文件的 `RBAC_demo` 目录下。

2.  **创建并激活虚拟环境 (推荐)**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安装依赖**:
    ```bash
    pip install fastapi uvicorn "python-multipart"
    ```

## 运行

在 `RBAC_demo` 目录下，运行以下命令启动 FastAPI 应用：

```bash
uvicorn rbac_controller:app --reload
```

*   `rbac_controller`: 指的是 `rbac_controller.py` 文件。
*   `app`: 指的是 `rbac_controller.py` 文件中创建的 FastAPI 实例。
*   `--reload`: 启用热重载，当代码发生变化时，服务器会自动重启。

应用启动后，您将在终端看到类似以下输出：
```
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: Started reloader process [xxxxx]
INFO: Started server process [xxxxx]
INFO: Waiting for application startup.
INFO: Application startup complete.
```


