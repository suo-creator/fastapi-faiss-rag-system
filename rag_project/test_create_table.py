# test_create_table.py
from app.core.database_models import engine, Base
from app.models.database_models import *

print("开始建表……")
Base.metadata.create_all(bind=engine)
print("建表完成！")
