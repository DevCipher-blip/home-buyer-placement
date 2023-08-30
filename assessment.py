from collections import deque

from helpers import read_input_data, calculate_buyer_scores, write_output_data


class Pearl:
    def __init__(self, input_file):
        self.neighborhoods, self.home_buyers = read_input_data(input_file)
        if not self.neighborhoods or len(self.home_buyers) % len(self.neighborhoods):
            raise ValueError("the number of home buyers must be a non-zero multiple of the number of neighborhoods")
        self.buyers_scores = calculate_buyer_scores(self.neighborhoods, self.home_buyers)
        self.neighborhood_limit = len(self.home_buyers) // len(self.neighborhoods)
        self.final_selections = {n['N']: [] for n in self.neighborhoods}

    def optimize_placements(self):
        # Buyer-proposing deferred acceptance: a buyer applies to their next choice, the
        # neighborhood keeps its best `neighborhood_limit` applicants and bumps the rest,
        # who then move on. The previous single pass over neighborhoods never let a bumped
        # buyer reach an earlier neighborhood and could place a leftover buyer twice.
        names = [n['N'] for n in self.neighborhoods]
        input_order = {b['H']: i for i, b in enumerate(self.home_buyers)}
        score = {
            (buyer, entry['neighborhood']): entry['score']
            for buyer, entries in self.buyers_scores.items()
            for entry in entries[:-1]
        }

        choices = {}
        for buyer in self.home_buyers:
            stated = list(dict.fromkeys(buyer['prefs']))
            unknown = [n for n in stated if n not in names]
            if unknown:
                raise ValueError(f"{buyer['H']} prefers unknown neighborhood(s): {', '.join(unknown)}")
            # Once stated preferences run out, fall back to the best-scoring remaining neighborhood
            rest = sorted((n for n in names if n not in stated), key=lambda n: -score[buyer['H'], n])
            choices[buyer['H']] = stated + rest

        held = {n: [] for n in names}
        next_choice = {b['H']: 0 for b in self.home_buyers}
        unplaced = deque(b['H'] for b in self.home_buyers)

        while unplaced:
            buyer = unplaced.popleft()
            neighborhood = choices[buyer][next_choice[buyer]]
            next_choice[buyer] += 1

            applicants = held[neighborhood]
            applicants.append(buyer)
            # Higher score wins; equal scores go to whoever appears first in the input
            applicants.sort(key=lambda b: (-score[b, neighborhood], input_order[b]))
            if len(applicants) > self.neighborhood_limit:
                unplaced.append(applicants.pop())

        self.final_selections = {n: [(b, score[b, n]) for b in held[n]] for n in names}

    def generate_output(self, filename):
        write_output_data(filename, self.final_selections)
