import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from endpoint import assistant_endpoint, chromadb_endpoint, datasource_endpoint ,chat_endpoint

api = FastAPI(
    title="سامانه ساخت دستیار هوشمند",
    description="سیستم ساخت دستیار هوشمند برای کسب‌وکارها با پشتیبانی از هر مدل زبانی",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# CORS (برای اتصال به Angular Panel Front-end)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5276", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routerهای RAG
api.include_router(chat_endpoint.router, prefix="/api")
api.include_router(assistant_endpoint.router, prefix="/api")
api.include_router(chromadb_endpoint.router, prefix="/api")
api.include_router(datasource_endpoint.router, prefix="/api")

# بررسی وجود فایل‌های استاتیک
static_dir = "app/static"
if os.path.exists(static_dir):
    # Mount پوشه فایل‌های استاتیک
    api.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Swagger UI آفلاین
    @api.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=api.openapi_url,
            title=f"{api.title} - Swagger UI",
            swagger_js_url="/static/swagger/dist/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger/dist/swagger-ui.css",
            swagger_favicon_url="/static/swagger/dist/favicon-32x32.png",
        )
    
    # ReDoc آفلاین (اختیاری)
    @api.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        from fastapi.openapi.docs import get_redoc_html
        return get_redoc_html(
            openapi_url=api.openapi_url,
            title=f"{api.title} - ReDoc",
            redoc_js_url="/static/swagger/dist/redoc.standalone.js",
        )
else:
    # اگر فایل‌های استاتیک وجود ندارند، از یک پیام ساده استفاده کن
    @api.get("/docs", include_in_schema=False)
    async def simple_docs():
        return HTMLResponse("""
        <html>
            <head><title>API Documentation</title></head>
            <body>
                <h1>📚 API Documentation</h1>
                <p>Swagger UI is not available in offline mode.</p>
                <p>Use Postman or check <code>/openapi.json</code> for the API schema.</p>
                <hr>
                <h3>Available Endpoints:</h3>
                <ul>
                    <li>POST /api/chat - RAG Chat</li>
                    <li>POST /api/assistant - Assistant endpoints</li>
                    <li>GET /api/collections - ChromaDB collections</li>
                    <li>POST /api/datasource - Data source management</li>
                </ul>
            </body>
        </html>
        """)

@api.get("/")
async def root():
    return {
        "message": "🚀 سامانه ساخت دستیار هوشمند RAG فعال است",
        "version": "1.0.0",
        "features": ["RAG Agentic", "چند مدل زبانی", "ChromaDB", "LangGraph"],
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

if __name__ == "__main__":
    #for debugging in vscode, use this line:
    #uvicorn.run("main:api", host="0.0.0.0", port=8008, reload=True)
    #for production, use this line:
    uvicorn.run("main:api", host="0.0.0.0", port=8008)