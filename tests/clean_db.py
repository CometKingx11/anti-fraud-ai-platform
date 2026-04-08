"""
清理数据库中的提交记录
"""

from app import create_app, db
from config.settings import config
import os

app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

with app.app_context():
    from app.models.submission import Submission

    submissions = Submission.query.all()
    print(f'当前有 {len(submissions)} 条提交记录')

    if submissions:
        for s in submissions:
            db.session.delete(s)
        db.session.commit()
        print('✓ 已删除所有提交记录')
    else:
        print('没有需要删除的记录')

    print('数据库清理完成！')
