
from app.core.database_models import Base,engine
from app.models.database_models import Conversation

Base.metadata.create_all(engine)
print('数据表创建完成')