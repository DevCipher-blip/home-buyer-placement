import unittest

class TestFileContent(unittest.TestCase):
  def test_file_content(self):
    expected_content = "N0: H5(161) H11(154) H2(128) H4(122)\nN1: H9(23) H8(21) H7(20) H1(18)\nN2: H6(128) H3(120) H10(86) H0(83)\n"
    
    with open('generated_output.txt', 'r') as file:
      file_content = file.read()

      self.assertEqual(file_content, expected_content)
