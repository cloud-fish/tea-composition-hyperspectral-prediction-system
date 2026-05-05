import uvicorn
import sys
import os

# 将当前目录加入 sys.path 以便导入 app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
