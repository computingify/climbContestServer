import threading
from climb_contest.models import Success, Climber, Bloc, climber_category_bloc, db

class Processor:
    
    MAX_BLOC_VALUE = 1000
    
    def run(self, categories_to_update):
        """Run algorithm to calculate the contest result based on the category"""
        # Liste tous les grimpeurs de la catégorie
        climbers = Climber.query.filter_by(category=categories_to_update).all()
        
        # climber_category_bloc is an association Table, so use db.session to join with Bloc
        blocs = db.session.query(Bloc).join(
            climber_category_bloc, Bloc.id == climber_category_bloc.c.bloc_id
        ).filter(climber_category_bloc.c.category == categories_to_update).all()
        # First of all, reset all climber scores to zero
        for climber in climbers:
            climber.score = 0
        # Caluclate the blocs scores based on the number of successes
        for bloc in blocs:
            succ_count = db.session.query(Success).join(Climber, Success.climber_id == Climber.id)\
                .filter(Success.bloc_id == bloc.id, Climber.category == categories_to_update).count()
            value = self.MAX_BLOC_VALUE / succ_count if succ_count > 0 else 0
            
            # For each climber who succeeded on this bloc, update their score in the Climber table
            successes = db.session.query(Success).join(Climber, Success.climber_id == Climber.id)\
                .filter(Success.bloc_id == bloc.id, Climber.category == categories_to_update).all()
            for success in successes:
                climber = success.climber
                climber.score += value
                db.session.add(climber)
        db.session.commit()
        
        # Now create rankings based on updated climber scores
        ranking = []
        for climber in climbers:
            ranking.append({
                "id": climber.id,
                "name": climber.name,
                "bib": climber.bib,
                "club": climber.club,
                "category": climber.category,
                "score": climber.score
            })
        # Sort by score descending
        ranking.sort(key=lambda x: x["score"], reverse=True)
        return ranking

processor = Processor()
