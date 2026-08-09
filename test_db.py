from rag_project.app.core.database_models import engine, Base
from rag_project.app.models import *

# 只是测试连接，不会重复新建表
Base.metadata.create_all(bind=engine)
print("✅数据库连接正常，表已经存在")

