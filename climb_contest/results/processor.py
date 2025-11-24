import threading
from climb_contest.models import BlocScore, Success, Climber, Bloc, climber_category_bloc, db

class Processor:
    def run(self, categories_to_update):
        """Run algorithm to calculate the contest result based on the category"""
        # Liste tous les grimpeurs de la catégorie
        climbers = Climber.query.filter_by(category=categories_to_update).all()
        # climber_category_bloc is an association Table, so use db.session to join with Bloc
        blocs = db.session.query(Bloc).join(
            climber_category_bloc, Bloc.id == climber_category_bloc.c.bloc_id
        ).filter(climber_category_bloc.c.category == categories_to_update).all()
        
        print(f"Processing category: {categories_to_update} with {len(climbers)} climbers and {len(blocs)} blocs")
        print(f"Climbers: {[c.name for c in climbers]}")
        print(f"Blocs: {[b.tag for b in blocs]}")
        
        ranking = []
        for climber in climbers:
            # Liste des succès du grimpeur
            successes = Success.query.filter_by(climber_id=climber.id).all()
            print(f"Climber '{climber.name}' has {len(successes)} successes: {[s.bloc_id for s in successes]}")
            score_total = 0
            for success in successes:
                bloc_score = BlocScore.query.filter_by(bloc_id=success.bloc_id, category=categories_to_update).first()
                if bloc_score:
                    score_total += bloc_score.value
            # Ajoute toutes les infos du grimpeur + score
            ranking.append({
                "id": climber.id,
                "name": climber.name,
                "bib": climber.bib,
                "club": climber.club,
                "category": climber.category,
                "score": score_total
            })
        # Trie par score décroissant
        ranking.sort(key=lambda x: x["score"], reverse=True)
        return ranking

processor = Processor()
