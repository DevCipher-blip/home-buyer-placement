from helpers import read_input_data, calculate_buyer_scores, generate_selection, write_output_data


class Pearl:
    def __init__(self, input_file):
        self.neighborhoods, self.home_buyers = read_input_data(input_file)
        self.buyers_scores = calculate_buyer_scores(self.neighborhoods, self.home_buyers)
        self.neighborhood_limit = len(self.home_buyers) // len(self.neighborhoods)
        self.final_selections = {n['N']: [] for n in self.neighborhoods}
        self.remaining_buyers = []
        self.selected_buyers = []
        self.buyer_selections = []

    def optimize_placements(self):
        for index, neighborhood in enumerate(self.neighborhoods):
            self.buyer_selections = []
            self.check_first_preference(neighborhood)
            self.handle_remaining_buyers(index, neighborhood)

            # Sort selected buyers based on their scores, in descending order
            self.buyer_selections.sort(key=lambda item: item['score'], reverse=True)

            self.check_neighborhood_limit()
            self.update_output()

        self.handle_leftover_buyers()

    def check_first_preference(self, neighborhood):
        for buyer, buyer_val in self.buyers_scores.items():
            # Check if the buyer with the maximum score in a neighborhood also has it as their first preference
            if buyer_val[-1][0] == neighborhood['N']:
                self.buyer_selections.append(generate_selection(neighborhood, buyer, buyer_val))

    def handle_remaining_buyers(self, index, neighborhood):
        # For the buyers that got excluded from their last preference due to upper limit restrictions
        for buyer in self.remaining_buyers:
            buyer_details = self.buyers_scores[buyer['buyer']]

            # Consider next preference and add accordingly
            if buyer_details[-1][1] == neighborhood['N']:
                self.buyer_selections.append(generate_selection(neighborhood, buyer['buyer'], buyer_details))

    def check_neighborhood_limit(self):
        # Place an upper limit to ensure number of buyers are evenly distributed
        if len(self.buyer_selections) > self.neighborhood_limit:
            self.remaining_buyers.extend(self.buyer_selections[self.neighborhood_limit:])
            self.buyer_selections = self.buyer_selections[:self.neighborhood_limit]

    def update_output(self):
        # Add the current neighborhood buyers to final output
        for buyer in self.buyer_selections:
            self.final_selections[buyer['neighborhood']].append((buyer['buyer'], buyer['score']))
            self.selected_buyers.append(buyer['buyer'])

    def handle_leftover_buyers(self):
        for buyer, buyer_val in self.buyers_scores.items():
            # For buyers that have not yet been placed in any neighborhood
            if buyer not in self.selected_buyers:
                # We go over their preferences and place in best available neighborhood
                for neighborhood in buyer_val[-1]:
                    if len(self.final_selections[neighborhood]) < self.neighborhood_limit:
                        self.final_selections[neighborhood].append(
                            (buyer, [b['score'] for b in buyer_val[:-1] if b['neighborhood'] == neighborhood][0]))

    def generate_output(self, filename):
        # Generate output file
        write_output_data(filename, self.final_selections)
