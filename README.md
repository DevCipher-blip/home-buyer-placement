# Buyer allocation walkthrough

## Work through a placement case

Read [input.txt](input.txt), follow scoring and selection in [helpers.py](helpers.py), and compare the result with [generated_output.txt](generated_output.txt). [assessment.py](assessment.py) holds the allocation object used by this version of the exercise.

The interesting questions are deterministic ordering, ties, exhausted choices, and invalid input. An example allocation is evidence of a particular scoring procedure, so fairness or global-optimality claims need a separate specification and tests.

## Requirements

- Python 3

## Getting Started

1. **Clone the repository**:
    > git clone <repository-url> pearl-certification-assessment

2. **Move into the repository directory**:
   > cd pearl-certification-assessment

3. **Run the application**:

    > python main.py

&nbsp;

The code will generate an output file named `generated_output.txt`, containing the optimal placement of home buyers in neighborhoods.

## Running test cases

Running the code by following the above steps will also automatically run an associated test, which asserts that the generated output file is correct.

To manually run the tests (after the output file to be tested has been generated), run the following:

  > python -m unittest discover tests
