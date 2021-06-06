import unittest
from hints import HintGenerator



class TestHintGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestHintGenerator.h1 = HintGenerator(5)
        TestHintGenerator.h2 = HintGenerator(24)
        TestHintGenerator.h3 = HintGenerator(1)
        TestHintGenerator.h4 = HintGenerator(0)
        TestHintGenerator.h5 = HintGenerator(-16)
        TestHintGenerator.h6 = HintGenerator(-1000)
        TestHintGenerator.h7 = HintGenerator(357)
        
        TestHintGenerator.hint_objs = [
            TestHintGenerator.h1,
            TestHintGenerator.h2,
            TestHintGenerator.h3,
            TestHintGenerator.h4,
            TestHintGenerator.h5,
            TestHintGenerator.h6,
            TestHintGenerator.h7
        ]
    
    def tearDown(self):
        for obj in TestHintGenerator.hint_objs:
            obj.hints.clear()
    
    def test_check_greater_or_less(self):
        self.assertEqual(TestHintGenerator.h1.check_greater_or_less(2), "Nice try! Higher.")
        self.assertEqual(TestHintGenerator.h1.check_greater_or_less(8), "Nice try! Lower.")
        self.assertEqual(TestHintGenerator.h5.check_greater_or_less(-17), "Nice try! Higher.")
        self.assertEqual(TestHintGenerator.h5.check_greater_or_less(0), "Nice try! Lower.")
        
        with self.assertRaises(TypeError):
            TestHintGenerator.h2.check_greater_or_less()
    
    def test_check_factors(self):
        TestHintGenerator.h2._check_factors()
        self.assertIn("Nice try!  Hint: It is divisible by 2.", TestHintGenerator.h2.hints)
        self.assertIn("Nice try!  Hint: It is divisible by 3.", TestHintGenerator.h2.hints)
        self.assertIn("Nice try!  Hint: It is divisible by 4.", TestHintGenerator.h2.hints)
        self.assertIn("Nice try!  Hint: It is divisible by 6.", TestHintGenerator.h2.hints)
        self.assertIn("Nice try!  Hint: It is divisible by 8.", TestHintGenerator.h2.hints)
        self.assertIn("Nice try!  Hint: It is divisible by 12.", TestHintGenerator.h2.hints)
        
        self.assertIn("Nice try!  Hint: It has 8 factors.", TestHintGenerator.h2.hints)
        
        self.assertIn("Nice try!  Hint: All of its digits are factors.", TestHintGenerator.h2.hints)
        self.assertEqual(len(TestHintGenerator.h2.hints), 8)
        
        TestHintGenerator.h7._check_factors()
        self.assertIn("Nice try!  Hint: 2 of its digits are factors.", TestHintGenerator.h7.hints)
        
        TestHintGenerator.h1._check_factors()
        self.assertEqual(len(TestHintGenerator.h1.hints), 0)
    
    def test_check_multiples(self):
        TestHintGenerator.h1._check_multiples(filter_results=False)
        self.assertIn("Nice try!  Hint: 5 is a multiple.", TestHintGenerator.h1.hints)
        self.assertIn("Nice try!  Hint: 10 is a multiple.", TestHintGenerator.h1.hints)
        self.assertIn("Nice try!  Hint: 15 is a multiple.", TestHintGenerator.h1.hints)
        self.assertIn("Nice try!  Hint: 20 is a multiple.", TestHintGenerator.h1.hints)
        self.assertIn("Nice try!  Hint: 25 is a multiple.", TestHintGenerator.h1.hints)
        self.assertEqual(len(TestHintGenerator.h1.hints), 5)
        
        TestHintGenerator.h5._check_multiples()
        h5_multiples = [
            "Nice try!  Hint: -16 is a multiple.",
            "Nice try!  Hint: -32 is a multiple.",
            "Nice try!  Hint: -48 is a multiple.",
            "Nice try!  Hint: -64 is a multiple.",
            "Nice try!  Hint: -80 is a multiple."
        ]
        self.assertEqual(len(TestHintGenerator.h5.hints), 2)
        for hint in TestHintGenerator.h5.hints:
            self.assertIn(hint, h5_multiples)
            
        TestHintGenerator.h4._check_multiples()
        self.assertIn("Nice try!  Hint: 0 is a multiple.", TestHintGenerator.h4.hints)
        self.assertEqual(len(TestHintGenerator.h4.hints), 1)
    
    def test_check_prime(self):
        TestHintGenerator.h1._check_prime()
        self.assertIn("Nice try!  Hint: It is a prime number.", TestHintGenerator.h1.hints)
        self.assertEqual(len(TestHintGenerator.h1.hints), 1)
        TestHintGenerator.h3._check_prime()
        self.assertNotIn("Nice try!  Hint: It is a prime number.", TestHintGenerator.h3.hints)
        self.assertEqual(len(TestHintGenerator.h3.hints), 0)
        TestHintGenerator.h4._check_prime()
        self.assertNotIn("Nice try!  Hint: It is a prime number.", TestHintGenerator.h4.hints)
        self.assertEqual(len(TestHintGenerator.h4.hints), 0)
        
        TestHintGenerator.h2._check_prime()
        self.assertIn("Nice try!  Hint: It has 2 prime factor(s).", TestHintGenerator.h2.hints)
        
        self.assertIn("Nice try!  Hint: 1 of its digits is a prime number.", TestHintGenerator.h2.hints)
        self.assertEqual(len(TestHintGenerator.h2.hints), 2)
        TestHintGenerator.h5._check_prime()
        self.assertIn("Nice try!  Hint: None of its digits are prime numbers.", TestHintGenerator.h5.hints)
        self.assertEqual(len(TestHintGenerator.h5.hints), 1)
        TestHintGenerator.h7._check_prime()
        self.assertIn("Nice try!  Hint: All of its digits are prime numbers.", TestHintGenerator.h7.hints)
        self.assertEqual(len(TestHintGenerator.h7.hints), 2)
    
    def test_check_even_odd(self):
        TestHintGenerator.h1._check_even_odd()
        self.assertIn("Nice try!  Hint: It is an odd number.", TestHintGenerator.h1.hints)
        self.assertEqual(len(TestHintGenerator.h1.hints), 1)
        TestHintGenerator.h6._check_even_odd()
        self.assertIn("Nice try!  Hint: It is an even number.", TestHintGenerator.h6.hints)
        self.assertEqual(len(TestHintGenerator.h6.hints), 1)
    
        TestHintGenerator.h7._check_even_odd()
        self.assertIn("Nice try!  Hint: All of its digits are odd.", TestHintGenerator.h7.hints)
        self.assertEqual(len(TestHintGenerator.h7.hints), 2)
        TestHintGenerator.h2._check_even_odd()
        self.assertIn("Nice try!  Hint: All of its digits are even.", TestHintGenerator.h2.hints)
        self.assertEqual(len(TestHintGenerator.h2.hints), 2)
    
        TestHintGenerator.h5._check_even_odd()
        self.assertEqual(len(TestHintGenerator.h5.hints), 1)
    
    def test_check_perfect_square(self):
        TestHintGenerator.h3._check_perfect_square()
        self.assertIn("Nice try!  Hint: It is a perfect square.", TestHintGenerator.h3.hints)
        self.assertEqual(len(TestHintGenerator.h3.hints), 1)
        TestHintGenerator.h4._check_perfect_square()
        self.assertIn("Nice try!  Hint: It is a perfect square.", TestHintGenerator.h4.hints)
        self.assertEqual(len(TestHintGenerator.h4.hints), 1)
        
        TestHintGenerator.h1._check_perfect_square()
        self.assertNotIn("Nice try!  Hint: It is a perfect square.", TestHintGenerator.h1.hints)
        self.assertEqual(len(TestHintGenerator.h1.hints), 0)
        TestHintGenerator.h5._check_perfect_square()
        self.assertNotIn("Nice try!  Hint: It is a perfect square.", TestHintGenerator.h5.hints)
        self.assertEqual(len(TestHintGenerator.h5.hints), 1)
        
        TestHintGenerator.h2._check_perfect_square()
        self.assertIn("Nice try!  Hint: 1 of its digits is a perfect square.", TestHintGenerator.h2.hints)
        self.assertEqual(len(TestHintGenerator.h2.hints), 1)
        TestHintGenerator.h6._check_perfect_square()
        self.assertIn("Nice try!  Hint: All of its digits are perfect squares.", TestHintGenerator.h6.hints)
        self.assertEqual(len(TestHintGenerator.h6.hints), 1)
        TestHintGenerator.h7._check_perfect_square()
        self.assertIn("Nice try!  Hint: None of its digits are perfect squares.", TestHintGenerator.h7.hints)
        self.assertEqual(len(TestHintGenerator.h7.hints), 1)
    
    def test_check_digit_sum(self):
        TestHintGenerator.h2._check_digit_sum()
        self.assertIn("Nice try!  Hint: The sum of the digits is 6.", TestHintGenerator.h2.hints)
        self.assertEqual(len(TestHintGenerator.h2.hints), 1)
        TestHintGenerator.h5._check_digit_sum()
        self.assertIn("Nice try!  Hint: The sum of the digits is 7.", TestHintGenerator.h5.hints)
        self.assertEqual(len(TestHintGenerator.h5.hints), 1)
        TestHintGenerator.h6._check_digit_sum()
        self.assertIn("Nice try!  Hint: The sum of the digits is 1.", TestHintGenerator.h6.hints)
        self.assertEqual(len(TestHintGenerator.h6.hints), 1)
        
        TestHintGenerator.h1._check_digit_sum()
        self.assertEqual(len(TestHintGenerator.h1.hints), 0)
    
    def test_check_digit_length(self):
        TestHintGenerator.h6._check_digit_length()
        self.assertIn("Nice try!  Hint: It is a 4-digit number.", TestHintGenerator.h6.hints)
        self.assertEqual(len(TestHintGenerator.h6.hints), 1)
        
        TestHintGenerator.h1._check_digit_length()
        self.assertEqual(len(TestHintGenerator.h1.hints), 0)
        TestHintGenerator.h2._check_digit_length()
        self.assertEqual(len(TestHintGenerator.h2.hints), 0)
    
    def test_prime_count(self):
        self.assertEqual(TestHintGenerator.h1._prime_count([2]), 1)
        self.assertEqual(TestHintGenerator.h1._prime_count([5, 7]), 2)
        self.assertEqual(TestHintGenerator.h1._prime_count([8, 9, 10]), 0)
        self.assertEqual(TestHintGenerator.h1._prime_count([0, 1, 2]), 1)
        self.assertEqual(TestHintGenerator.h1._prime_count([3, 3]), 2)
        self.assertEqual(TestHintGenerator.h1._prime_count([11, 13, 17, 19]), 4)
    
        with self.assertRaises(TypeError):
            TestHintGenerator.h1._prime_count()

    def test_is_factor(self):
        self.assertTrue(TestHintGenerator.h1._is_factor(6, 3))
        self.assertFalse(TestHintGenerator.h1._is_factor(9, 4))
        self.assertTrue(TestHintGenerator.h1._is_factor(13, 13))
        self.assertTrue(TestHintGenerator.h1._is_factor(13, 1))
        self.assertTrue(TestHintGenerator.h1._is_factor(-48, -6))
        self.assertFalse(TestHintGenerator.h1._is_factor(-48, -10))
        self.assertTrue(TestHintGenerator.h1._is_factor(-48, 8))
        self.assertFalse(TestHintGenerator.h1._is_factor(3, 6))
        self.assertTrue(TestHintGenerator.h1._is_factor(0, 2))
        
        with self.assertRaises(ZeroDivisionError):
            TestHintGenerator.h1._is_factor(1, 0)
        
        with self.assertRaises(TypeError):
            TestHintGenerator.h1._is_factor()



if __name__ == '__main__':
    unittest.main()