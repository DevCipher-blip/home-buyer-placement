import unittest
from tests import TestFileContent

def read_input_data(filename):
  neighborhoods, home_buyers = [], []

  with open(filename, 'r') as file:
    for line in file:
      parts = line.split()
      data_dict = {}

      data_dict[parts[0]] = parts[1]

      for val in parts[2:5]:
        key, value = val.split(':')
        data_dict[key] = int(value)

      if parts[0] == 'N':
        neighborhoods.append(data_dict)
      elif parts[0] == 'H':
        # Since home buyer have an additional attribute of preferences, we save that as well
        data_dict['prefs'] = parts[5].split('>')
        home_buyers.append(data_dict)

  return neighborhoods, home_buyers

def write_output_data(filename, selections):
  with open(filename, 'w') as file:
    for neighborhood, assigned_buyers in selections.items():
      assigned_buyers.sort(key=lambda x: x[1], reverse=True)

      # Write output data to file in expected format
      file.write(f"{neighborhood}: {' '.join([f'{h}({s})' for h, s in assigned_buyers])}\n")

def calculate_buyer_scores(neighborhoods, home_buyers):
  """
  Calculate compatibility scores between home buyers and neighborhoods by using the
  dot product of the home buyer's goals and the neighborhood scores.
  """
  buyers_scores = {}

  for buyer in home_buyers:
    current_scores = []

    for neighborhood in neighborhoods:
      current_scores.append({
        'neighborhood': neighborhood['N'],
        'score': buyer['E'] * neighborhood['E'] + buyer['W'] * neighborhood['W'] + buyer['R'] * neighborhood['R'],
      })

    # Sort buyers by their scores in each neighborhood in descending order
    buyers_scores[buyer['H']] = sorted(current_scores, key=lambda item: item['score'], reverse=True)
    buyers_scores[buyer['H']].append(buyer['prefs'])
    
  return buyers_scores

def generate_selection(neighborhood, buyer, buyer_value):
  return {
    'neighborhood': neighborhood['N'],
    'buyer': buyer,
    'score': [b['score'] for b in buyer_value[:-1] if b['neighborhood'] == neighborhood['N']][0]
  }

def run_tests():
  test_suite = unittest.TestSuite()
  test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFileContent))

  test_runner = unittest.TextTestRunner()
  test_result = test_runner.run(test_suite)

  if test_result.wasSuccessful():
    print("Generated output file is correct.")
  else:
    print("Generated output file does not match the expected output.")
