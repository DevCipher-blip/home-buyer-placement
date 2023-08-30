from assessment import Pearl
from helpers import run_tests

if __name__ == '__main__':
  assessment = Pearl('input.txt')
  assessment.optimize_placements()
  assessment.generate_output('generated_output.txt')

  # Run tests to check generated output
  run_tests()
