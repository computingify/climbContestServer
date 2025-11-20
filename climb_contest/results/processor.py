import threading
from climb_contest.models import BlocScore, Success, Climber, Bloc, climber_category_bloc, db

class Processor:
    def run(self, categories_to_update):
        """Run algorithm to calculate the contest result based on the category"""
        # Liste tous les grimpeurs de la catégorie
        climbers = Climber.query.filter_by(category=categories_to_update).all()
        classement = []
        for climber in climbers:
            # Liste des succès du grimpeur
            successes = Success.query.filter_by(climber_id=climber.id).all()
            score_total = 0
            for success in successes:
                bloc_score = BlocScore.query.filter_by(bloc_id=success.bloc_id, category=categories_to_update).first()
                if bloc_score:
                    score_total += bloc_score.value
            # Ajoute toutes les infos du grimpeur + score
            classement.append({
                "id": climber.id,
                "name": climber.name,
                "bib": climber.bib,
                "club": climber.club,
                "category": climber.category,
                "score": score_total
            })
        # Trie par score décroissant
        classement.sort(key=lambda x: x["score"], reverse=True)
        return classement

processor = Processor()
