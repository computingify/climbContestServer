from datetime import datetime
from models import Success

class Result:
    def __init__(self, db):
        self.db = db
        
    def record_success(self, climber_id, bloc_id):
        try:
            success = Success(
                climber_id=climber_id,
                bloc_id=bloc_id,
                timestamp=datetime.utcnow(),
            )
            self.db.session.add(success)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            print(f"Failed to record success: {e}")
            
    # def extract_by_category(self, category):
        