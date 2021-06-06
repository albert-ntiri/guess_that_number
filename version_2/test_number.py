import unittest
from number import Number



class TestNumber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestNumber.num_obj = Number()
    
    def setUp(self):
        self.test_case_1 = '3'
        self.test_case_2 = '.5'
        self.test_case_3 = '0'
        self.test_case_4 = '-10'
        self.test_case_5 = '-2.1'
        self.test_case_6 = 'a'
        self.test_case_7 = ''
    
    def test_is_integer(self):
        self.assertTrue(TestNumber.num_obj._is_integer(self.test_case_1))
        self.assertFalse(TestNumber.num_obj._is_integer(self.test_case_2))
        self.assertTrue(TestNumber.num_obj._is_integer(self.test_case_3))
        self.assertTrue(TestNumber.num_obj._is_integer(self.test_case_4))
        self.assertFalse(TestNumber.num_obj._is_integer(self.test_case_5))
        self.assertFalse(TestNumber.num_obj._is_integer(self.test_case_6))
        self.assertFalse(TestNumber.num_obj._is_integer(self.test_case_7))
        
        with self.assertRaises(TypeError):
            TestNumber.num_obj._is_integer()
    
    def test_convert_to_int(self):
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_1), 3)
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_2), False)
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_3), 0)
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_4), -10)
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_5), False)
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_6), False)
        self.assertEqual(TestNumber.num_obj.convert_to_int(self.test_case_7), False)
    
        with self.assertRaises(TypeError):
            TestNumber.num_obj.convert_to_int()
    
    def test_validate_range(self):
        self.assertEqual(TestNumber.num_obj.validate_range(('1', '10')), (1, 10))
        self.assertEqual(TestNumber.num_obj.validate_range(('0', '100')), (0, 100))
        self.assertEqual(TestNumber.num_obj.validate_range(('', '10')), 'invalid')
        self.assertEqual(TestNumber.num_obj.validate_range(('1', '')), 'invalid')
        self.assertEqual(TestNumber.num_obj.validate_range(('1', '5.5')), 'invalid')
        self.assertEqual(TestNumber.num_obj.validate_range(('10', '1')), 'comparison')
        self.assertEqual(TestNumber.num_obj.validate_range(('-10', '-1')), (-10, -1))
        self.assertEqual(TestNumber.num_obj.validate_range(('-1', '-10')), 'comparison')
        self.assertEqual(TestNumber.num_obj.validate_range(('', '')), 'missing')
        self.assertEqual(TestNumber.num_obj.validate_range(('5', '5')), 'comparison')
        self.assertEqual(TestNumber.num_obj.validate_range(('0', '0')), 'comparison')
        self.assertEqual(TestNumber.num_obj.validate_range(('a', 'b')), 'invalid')
    
        with self.assertRaises(TypeError):
            TestNumber.num_obj.validate_range()
    
    def test_generate_random_number(self):
        self.assertIn(TestNumber.num_obj.generate_random_number((1, 10)), range(1, 11))
        self.assertIn(TestNumber.num_obj.generate_random_number((1, 100)), range(1, 101))
        self.assertIn(TestNumber.num_obj.generate_random_number((1, 1000)), range(1, 1001))
        self.assertIn(TestNumber.num_obj.generate_random_number((0, 5)), range(0, 6))
        self.assertIn(TestNumber.num_obj.generate_random_number((-5, -1)), [-5,-4,-3,-2,-1])
        self.assertIn(TestNumber.num_obj.generate_random_number((-2, 2)), [-2,-1,0,1,2])
    
        with self.assertRaises(TypeError):
            TestNumber.num_obj.generate_random_number()
    
    def test_unique_random_numbers(self):
        numbers = TestNumber.num_obj.unique_random_numbers((1, 5), 2)
        self.assertEqual(len(numbers), 2)
        self.assertEqual(len(set(numbers)), len(numbers))
        for n in numbers:
            self.assertIn(n, range(1, 6))
    
        with self.assertRaises(TypeError):
            TestNumber.num_obj.unique_random_numbers()
    
    def test_pattern_match(self):
        text1 = "Nice try!  Hint: It is a 3-digit number."
        self.assertEqual(TestNumber.num_obj._pattern_match("\d+", text1, value=True), '3')
        text2 = "Nice try!  Hint: It has 2 prime factor(s)."
        self.assertEqual(TestNumber.num_obj._pattern_match("\d+", text2, value=True), '2')
        text3 = "Nice try!  Hint: All of its digits are prime numbers."
        self.assertTrue(TestNumber.num_obj._pattern_match("digits", text3))
        text4 = "Nice try!  Hint: It is a prime number."
        self.assertFalse(TestNumber.num_obj._pattern_match("digits", text4))
        text5 = "Nice try!  Hint: None of its digits are perfect squares."
        self.assertTrue(TestNumber.num_obj._pattern_match("None", text5))
        text6 = "Nice try!  Hint: 1 of its digits is a perfect square."
        self.assertFalse(TestNumber.num_obj._pattern_match("None", text6))
    
        with self.assertRaises(TypeError):
            TestNumber.num_obj._pattern_match()
    
    def test_validate_guess(self):
        hint1 = "Nice try!  Hint: It is divisible by 7."
        self.assertEqual(TestNumber.num_obj.validate_guess(21, hint1, "factor"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(10, hint1, "factor"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(7, hint1, "factor"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(0, hint1, "factor"), "good")
        hint2 = "Nice try!  Hint: It has 4 factors."
        self.assertEqual(TestNumber.num_obj.validate_guess(15, hint2, "factor"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(9, hint2, "factor"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(8, hint2, "factor"), "good")
        hint3 = "Nice try!  Hint: 1 of its digits is a factor."
        self.assertEqual(TestNumber.num_obj.validate_guess(63, hint3, "factor"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(27, hint3, "factor"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(36, hint3, "factor"), "bad")
        hint4 = "Nice try!  Hint: 30 is a multiple."
        self.assertEqual(TestNumber.num_obj.validate_guess(2, hint4, "multiple"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(4, hint4, "multiple"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(30, hint4, "multiple"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(0, hint4, "multiple"), "bad")
        hint5 = "Nice try!  Hint: It is a prime number."
        self.assertEqual(TestNumber.num_obj.validate_guess(5, hint5, "prime"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(1, hint5, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(0, hint5, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(6, hint5, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(-1, hint5, "prime"), "bad")
        hint6 = "Nice try!  Hint: It has 1 prime factor(s)."
        self.assertEqual(TestNumber.num_obj.validate_guess(9, hint6, "prime"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(18, hint6, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(32, hint6, "prime"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(2, hint6, "prime"), "good")
        hint7 = "Nice try!  Hint: It has 2 prime factor(s)."
        self.assertEqual(TestNumber.num_obj.validate_guess(33, hint7, "prime"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(25, hint7, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(12, hint7, "prime"), "good")
        hint8 = "Nice try!  Hint: None of its digits are prime numbers."
        self.assertEqual(TestNumber.num_obj.validate_guess(48, hint8, "prime"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(25, hint8, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(12, hint8, "prime"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(100, hint8, "prime"), "good")
        hint9 = "Nice try!  Hint: It is an odd number."
        self.assertEqual(TestNumber.num_obj.validate_guess(1, hint9, "even_odd"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(24, hint9, "even_odd"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(0, hint9, "even_odd"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(-5, hint9, "even_odd"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(-64, hint9, "even_odd"), "bad")
        hint10 = "Nice try!  Hint: All of its digits are even."
        self.assertEqual(TestNumber.num_obj.validate_guess(48, hint10, "even_odd"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(53, hint10, "even_odd"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(218, hint10, "even_odd"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(6, hint10, "even_odd"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(20000, hint10, "even_odd"), "good")
        hint11 = "Nice try!  Hint: It is a perfect square."
        self.assertEqual(TestNumber.num_obj.validate_guess(49, hint11, "perfect_square"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(27, hint11, "perfect_square"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(0, hint11, "perfect_square"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(1, hint11, "perfect_square"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(-4, hint11, "perfect_square"), "bad")
        hint12 = "Nice try!  Hint: 2 of its digits are perfect squares."
        self.assertEqual(TestNumber.num_obj.validate_guess(493, hint12, "perfect_square"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(6875, hint12, "perfect_square"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(49, hint12, "perfect_square"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(1, hint12, "perfect_square"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(114, hint12, "perfect_square"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(186, hint12, "perfect_square"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(-103, hint12, "perfect_square"), "good")
        hint13 = "Nice try!  Hint: The sum of the digits is 8."
        self.assertEqual(TestNumber.num_obj.validate_guess(26, hint13, "digit_sum"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(45, hint13, "digit_sum"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(440, hint13, "digit_sum"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(12131, hint13, "digit_sum"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(88, hint13, "digit_sum"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(8, hint13, "digit_sum"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(-53, hint13, "digit_sum"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(-31, hint13, "digit_sum"), "bad")
        hint14 = "Nice try!  Hint: It is a 3-digit number."
        self.assertEqual(TestNumber.num_obj.validate_guess(108, hint14, "digit_length"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(2455, hint14, "digit_length"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(222, hint14, "digit_length"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(69, hint14, "digit_length"), "bad")
        self.assertEqual(TestNumber.num_obj.validate_guess(-331, hint14, "digit_length"), "good")
        self.assertEqual(TestNumber.num_obj.validate_guess(-8, hint14, "digit_length"), "bad")

        with self.assertRaises(TypeError):
            TestNumber.num_obj.validate_guess()
    


if __name__ == '__main__':
    unittest.main()