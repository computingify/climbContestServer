import threading
from climb_contest.models import Climber, Bloc, Success, climber_category_bloc

class Processor:
    def __init__(self, config):
        self.config = config

    def run(self, categories_to_update):
        """Run algorithm to calculate the contest result based on the category"""
        print(f"Processing data for categories: {categories_to_update}")
        for category_to_update in categories_to_update:
            print(f"Processing data for category: {category_to_update}")
            # Correction : jointure avec Climber pour filtrer les Success par catégorie
            successes = (
                Success.query
                .join(Climber, Success.climber_id == Climber.id)
                .filter(Climber.category == category_to_update)
                .all()
            )
            print(f"Found {len(successes)} successes for category {category_to_update}")
            # ...tu peux traiter les succès ici...

        # # Process the data
        # climber_category_bloc = self.config['db'].get_climber_category_bloc()
        # for category in climber_category_bloc:
        #     for bloc_id in category['blocs']:
        #         success_climbers = self.config['db'].get_success_climbers(category['id'], bloc_id)
        #         for climber in success_climbers:
        #             # Recalculate climber's score
        #             climber_score = self.calculate_score(climber, bloc_id)
        #             self.update_climber_score(climber, climber_score)
        #             print(f"Handling data: {climber} {bloc_id}")

        def calculate_score(self, climber, bloc_id):
            # Implement the logic to calculate the score based on the climber and bloc_id
            return 0  # Placeholder for actual score calculation logic

        def update_climber_score(self, climber, score):
            # Implement the logic to update the climber's score in the database
            pass
        
        # Should run in dedicated thread
        # Aquired the mutex to access the buffer
        # Get the last buffer element
        # Release the mutex
        # Process the data
        ## Each Bloc should store the bloc score value per category
        ## List all Climber successed on the affected bloc
        ## Each Climber in the list we should recalculate his score. Based on the link in Climber to Success to access to Bloc and finally the bloc score
        ## Each Climber should have entry with score
        # print(f"Handling data: {climber} {bloc}")
    
    def add_success(self, success):
        """Bufferized success to be processed by another thread"""
        # Aquired the mutex to access the buffer
        # Add the success on the top of the buffer
        # Release the mutex
        print(f"Adding success: {success}")

