class Processor:
    def __init__(self, config):
        self.config = config

    def run(self, climber, bloc):
        """Process data stored in the buffer to calculate the final results"""
        # Should run in dedicated thread
        # Aquired the mutex to access the buffer
        # Get the last buffer element
        # Release the mutex
        # Process the data
        ## Each Bloc should store the bloc score value per category
        ## List all Climber successed on the affected bloc
        ## Each Climber in the list we should recalculate his score. Based on the link in Climber to Success to access to Bloc and finally the bloc score
        ## Each Climber should have entry with score
        print(f"Handling data: {climber} {bloc}")
    
    def add_success(self, success):
        """Bufferized success to be processed by another thread"""
        # Aquired the mutex to access the buffer
        # Add the success on the top of the buffer
        # Release the mutex
        print(f"Adding success: {success}")
        
        