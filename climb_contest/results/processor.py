import threading
import time
from datetime import datetime
from climb_contest.models import MAX_BLOC_VALUE, Success, Climber, Bloc, climber_category_bloc, db, Ranking

class Processor(threading.Thread):
    _SLEEP_TIME = 30 
    
    def __init__(self, app):
        super().__init__()
        self.daemon = True # Le thread se termine lorsque le programme principal se termine
        self.app = app
        self._stop_event = threading.Event()
        # Event to trigger manual update
        self.manual_update_event = threading.Event()
        
    def ranking_update_needed(self):
        """Signal that a ranking update is needed."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal de mise à jour reçu.")
        self.manual_update_event.set()
    
    def run(self):
        while not self._stop_event.is_set():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Start of processing loop (ID: {threading.get_ident()})")
            # if self.ranking_update_needed_flag:
            #     self.ranking_update_needed_flag = False
            print(f"[{datetime.now().strftime('%H:%M:%S')}] RUN processing")
            with self.app.app_context():
                try:
                    self._calculate_and_store_ranking()
                except Exception as e:
                    db.session.rollback()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ERREUR lors du calcul/stockage du classement : {e}")
            
            # Attend 15 secondes avant la prochaine exécution
            self.manual_update_event.clear() 
            self.manual_update_event.wait(self._SLEEP_TIME)
    
    def _calculate_and_store_ranking(self):
        """Récupère toutes les catégories, calcule et stocke le classement."""
        
        # NOTE: Vous aurez besoin d'une fonction pour récupérer toutes les catégories
        # Si vous utilisez un `handler`, vous devez l'importer et le rendre disponible.
        # Pour simplifier, on peut juste interroger la DB:
        categories_rows = db.session.query(Climber.category).distinct().order_by(Climber.category).all()
        categories = [c[0] for c in categories_rows if c[0]] # Liste des catégories existantes
        categories.append('scratch') # Ajoutez la catégorie scratch
        
        new_ranking_entries = []
        for category in categories:
            # 1. Calcul du classement pour la catégorie
            results = self.calculate(category, commit_score=True)
            
            # 2. Création des objets Ranking avec le rang
            for rank, climber_data in enumerate(results, 1):
                new_ranking_entries.append(
                    Ranking(
                        climber_id=climber_data["id"],
                        category=category,
                        rank=rank,
                        score=climber_data["score"]
                    )
                )
                # Update climber category_rank
                if category == 'scratch':
                    db.session.query(Climber).filter_by(id=climber_data["id"]).update({
                        'scratch_rank': rank
                    })
                elif category == climber_data["category"]:
                    db.session.query(Climber).filter_by(id=climber_data["id"]).update({
                        'category_rank': rank
                    })

        # 3. Mise à jour atomique de la table Ranking
        # Supprimer l'ancien classement
        db.session.query(Ranking).delete()
        
        # Insérer le nouveau classement
        db.session.bulk_save_objects(new_ranking_entries)
        
        # Valider la transaction
        db.session.commit()
        
    def stop(self):
        self._stop_event.set()
    
    def calculate(self, categories_to_update, commit_score=False):
        """Run algorithm to calculate the contest result based on the category.
        categories_to_update can be:
            - "scratch" or "all" or "all_categories" or "*" -> all categories
            - a string category name -> that single category
            - a list/tuple/set of category names -> those categories
            - "men" or "m" -> categories ending with " H"
            - "women" or "w" -> categories ending with " F"
        """
        # Normalize selector
        selector = categories_to_update
        is_all = False
        cat_list = None
        suffix = None
        
        # print(f'Processing categories: {selector}')

        if selector is None:
            is_all = True
        elif isinstance(selector, (list, tuple, set)):
            cat_list = list(selector)
        elif isinstance(selector, str):
            s = selector.strip().lower()
            if s in ("scratch", "all", "all_categories", "*"):
                is_all = True
            elif s in ("men", "m"):
                suffix = " H"
            elif s in ("women", "w"):
                suffix = " F"
            else:
                cat_list = [selector]

        # Build climber query
        climber_query = Climber.query
        if not is_all:
            if cat_list is not None:
                climber_query = climber_query.filter(Climber.category.in_(cat_list))
            elif suffix is not None:
                climber_query = climber_query.filter(Climber.category.like(f"%{suffix}"))
        climbers = climber_query.all()

        # blocs: join with climber_category_bloc and apply same category selection
        bloc_q = db.session.query(Bloc).join(
            climber_category_bloc, Bloc.id == climber_category_bloc.c.bloc_id
        )
        if not is_all:
            if cat_list is not None:
                bloc_q = bloc_q.filter(climber_category_bloc.c.category.in_(cat_list))
            elif suffix is not None:
                bloc_q = bloc_q.filter(climber_category_bloc.c.category.like(f"%{suffix}"))
        blocs = bloc_q.all()
        
        # First of all, reset all climber scores to zero
        for climber in climbers:
            climber.score = 0
            
        # Caluclate the blocs scores based on the number of successes
        for bloc in blocs:
            # Détermine la liste des catégories à filtrer
            if is_all:
                cat_filter = None
            elif cat_list is not None:
                cat_filter = cat_list
            elif suffix is not None:
                # Récupère toutes les catégories qui finissent par le suffix
                cat_filter = [c.category for c in climbers if c.category and c.category.endswith(suffix)]
            else:
                cat_filter = [selector] if selector else None

            query = db.session.query(Success).join(Climber, Success.climber_id == Climber.id)\
                .filter(Success.bloc_id == bloc.id)
            if cat_filter:
                query = query.filter(Climber.category.in_(cat_filter))
            succ_count = query.count()

            # Calculate bloc value
            value = round(MAX_BLOC_VALUE / succ_count if succ_count > 0 else 0)
            
            # print(f'Bloc {bloc.tag} ({bloc.id}) has {succ_count} successes for categories filter: {cat_filter} -> value = {value}')

            successes = db.session.query(Success).join(Climber, Success.climber_id == Climber.id)\
                .filter(Success.bloc_id == bloc.id)
            if cat_filter:
                successes = successes.filter(Climber.category.in_(cat_filter))
            successes = successes.all()
            for success in successes:
                climber = success.climber
                climber.score += value
                db.session.add(climber)
                
        if commit_score:
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
