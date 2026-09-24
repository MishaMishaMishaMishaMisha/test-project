from fastapi import FastAPI

from src.api.v1.routers import api_v1_router


app = FastAPI()

app.include_router(api_v1_router)

# from src.database.tables_manager import create_tables, drop_tables

# @app.get("/")
# async def root() -> str:
#     return "hello!!!"

# @app.get("/create_tables")
# async def create_tables():
#     await create_tables()
    
# @app.get("/drop_tables")
# async def drop_tables():
#     await drop_tables()
    

    
if __name__ == "__main__":
    
    print("<main file>")
    
    import uvicorn
    
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=8000,
                reload=True)