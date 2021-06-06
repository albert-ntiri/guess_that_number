import unittest
from application_text import AppText



class TestAppText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestAppText.app_text = AppText()
    
    def test_get_static_text(self):
        select_level_text = "Select a level of difficulty:"
        self.assertEqual(TestAppText.app_text.get_static_text(
            "label", "welcome_page", "select_level"), select_level_text)
        self.assertEqual(TestAppText.app_text.get_static_text(
            "button", "game_page", "enter_button"), "ENTER")
        
        with self.assertRaises(KeyError):
            TestAppText.app_text.get_static_text("label", "welcome_page", "enter_button")
            TestAppText.app_text.get_static_text("libel", "welcome_page", "select_level")
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_static_text()
    
    def test_get_guess_prompt_msg(self):
        self.assertEqual(TestAppText.app_text.get_guess_prompt_msg((1, 10)), 
                         "Guess a number between 1 and 10.")
        self.assertEqual(TestAppText.app_text.get_guess_prompt_msg((1, 100)), 
                         "Guess a number between 1 and 100.")
        self.assertEqual(TestAppText.app_text.get_guess_prompt_msg((1, 1000)), 
                         "Guess a number between 1 and 1000.")
        self.assertEqual(TestAppText.app_text.get_guess_prompt_msg((-10, 0)), 
                         "Guess a number between -10 and 0.")
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_guess_prompt_msg()
    
    def test_get_status(self):
        self.assertEqual(TestAppText.app_text.get_status(10), "Guesses Remaining: 10")
        self.assertEqual(TestAppText.app_text.get_status(3), "Guesses Remaining: 3")
        self.assertEqual(TestAppText.app_text.get_status(0), "Guesses Remaining: 0")
        
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_status()
    
    def test_get_error_msg(self):
        text1 = "Both values must be integers."
        self.assertEqual(TestAppText.app_text.get_error_msg(
            "welcome_page", "range_entry", "invalid"), text1)
        text2 = "Your guess is out of range. Please try again."
        self.assertEqual(TestAppText.app_text.get_error_msg(
            "game_page", "guess_entry", "out_of_range"), text2)
        
        with self.assertRaises(KeyError):
            TestAppText.app_text.get_error_msg("game_page", "range_entry", "out_of_range")
            TestAppText.app_text.get_error_msg("game_page", "range_entr", "invalid")
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_error_msg()
    
    def test_get_static_hint(self):
        text1 = "Nice try!  Hint: It is a perfect square."
        self.assertEqual(TestAppText.app_text.get_static_hint(
            "perfect_square", "number"), text1)
        text2 = "Nice try! Lower."
        self.assertEqual(TestAppText.app_text.get_static_hint(
            "greater_less", "number", "less"), text2)
        text3 = "Nice try!  Hint: All of its digits are even."
        self.assertEqual(TestAppText.app_text.get_static_hint(
            "even_odd", "digits", "even"), text3)
        
        with self.assertRaises(KeyError):
            TestAppText.app_text.get_static_hint("even_odd", "digit", "even")
            TestAppText.app_text.get_static_hint("perfect_square", "number", "perfect_square")
            TestAppText.app_text.get_static_hint("greater_less", "number")
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_static_hint()
    
    def test_get_value_based_hint(self):
        text1 = "Nice try!  Hint: 15 is a multiple."
        self.assertEqual(TestAppText.app_text.get_value_based_hint(
            "multiple", "number", 15), text1)
        text2 = "Nice try!  Hint: It has 6 factors."
        self.assertEqual(TestAppText.app_text.get_value_based_hint(
            "factor", "number", 6, "count"), text2)
        
        with self.assertRaises(KeyError):
            TestAppText.app_text.get_value_based_hint("multiple", "numer", 15)
            TestAppText.app_text.get_value_based_hint("factor", "number", 6)
            TestAppText.app_text.get_value_based_hint("factor", "number", 6, "individual")
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_value_based_hint()
    
    def test_get_count_based_hint(self):
        text1 = "Nice try!  Hint: All of its digits are factors."
        self.assertEqual(TestAppText.app_text.get_count_based_hint(
            "factor", 2, 2), text1)
        text2 = "Nice try!  Hint: 1 of its digits is a prime number."
        self.assertEqual(TestAppText.app_text.get_count_based_hint(
            "prime", 2, 1), text2)
        text3 = "Nice try!  Hint: 2 of its digits are perfect squares."
        self.assertEqual(TestAppText.app_text.get_count_based_hint(
            "perfect_square", 3, 2), text3)
        text4 = "Nice try!  Hint: None of its digits are factors."
        self.assertEqual(TestAppText.app_text.get_count_based_hint(
            "factor", 4, 0), text4)
        self.assertIsNone(TestAppText.app_text.get_count_based_hint(
            "perfect_square", 2, 3))
        
        with self.assertRaises(KeyError):
            TestAppText.app_text.get_count_based_hint("multiple", 2, 2)
            TestAppText.app_text.get_count_based_hint("perfect-square", 3, 2)
            TestAppText.app_text.get_count_based_hint("prime", 1, 2)
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_count_based_hint()
    
    def test_get_hint_type(self):
        text1 = "Nice try!  Hint: It is divisible by 5."
        self.assertEqual(TestAppText.app_text.get_hint_type(text1), "factor")
        text2 = "Nice try!  Hint: 8 is a multiple."
        self.assertEqual(TestAppText.app_text.get_hint_type(text2), "multiple")
        text3 = "Nice try!  Hint: It has 2 prime factor(s)."
        self.assertEqual(TestAppText.app_text.get_hint_type(text3), "prime")
        text4 = "Nice try!  Hint: All of its digits are even."
        self.assertEqual(TestAppText.app_text.get_hint_type(text4), "even_odd")
        text5 = "Nice try!  Hint: All of its digits are perfect squares."
        self.assertEqual(TestAppText.app_text.get_hint_type(text5), "perfect_square")
        text6 = "Nice try!  Hint: The sum of the digits is 12."
        self.assertEqual(TestAppText.app_text.get_hint_type(text6), "digit_sum")
        text7 = "Nice try!  Hint: It is a 3-digit number."
        self.assertEqual(TestAppText.app_text.get_hint_type(text7), "digit_length")
        text8 = "Nice try! Higher."
        self.assertEqual(TestAppText.app_text.get_hint_type(text8), "greater_less")
        self.assertIsNone(TestAppText.app_text.get_hint_type(""))
    
        with self.assertRaises(TypeError):
            TestAppText.app_text.get_hint_type()
    
    def test_get_feedback(self):
        pass
    
    def test_get_general_feedback(self):
        text1 = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
        self.assertEqual(TestAppText.app_text._get_general_feedback("multiple"), text1)
        text2 = "Feedback:\nSome of your guesses did not match the hints.  For example: even/odd numbers."
        self.assertEqual(TestAppText.app_text._get_general_feedback("even_odd"), text2)
        text3 = "Feedback:\nSome of your guesses did not match the hints.  For example: n-digit numbers."
        self.assertEqual(TestAppText.app_text._get_general_feedback("digit_length"), text3)
    
        with self.assertRaises(KeyError):
            TestAppText.app_text._get_general_feedback("digit-sum")
            TestAppText.app_text._get_general_feedback("factors")
        
        with self.assertRaises(TypeError):
            TestAppText.app_text._get_general_feedback()
    
    def test_get_specific_feedback(self):
        hint1 = "Nice try!  Hint: 12 is a multiple."
        text1 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 12 is a multiple."'
        self.assertEqual(TestAppText.app_text._get_specific_feedback(5, hint1), text1)
        hint2 = "Nice try!  Hint: It is an odd number."
        text2 = 'Your guess, 0, did not match the hint: "Nice try!  Hint: It is an odd number."'
        self.assertEqual(TestAppText.app_text._get_specific_feedback(0, hint2), text2)
    
        with self.assertRaises(TypeError):
            TestAppText.app_text._get_specific_feedback()
    
    def test_get_description_feedback(self):
        description1 = "Multiple: TheÂ resultÂ ofÂ multiplying a number by an integer (not by a fraction)."
        text1 = "Remember:\nMultiple: TheÂ resultÂ ofÂ multiplying a number by an integer (not by a fraction)."
        self.assertEqual(TestAppText.app_text._get_description_feedback(description1), text1)
        description2 = "Even: An integer that is a multiple of 2. The even numbers are { . . . , â€“4, â€“2, 0, 2, 4, 6, . . . }.\nOdd: An integer that is not a multiple of 2. The odd numbers are { . . . , â€“3, â€“1, 1, 3, 5, . . . }."
        text2 = "Remember:\nEven: An integer that is a multiple of 2. The even numbers are { . . . , â€“4, â€“2, 0, 2, 4, 6, . . . }.\nOdd: An integer that is not a multiple of 2. The odd numbers are { . . . , â€“3, â€“1, 1, 3, 5, . . . }."
        self.assertEqual(TestAppText.app_text._get_description_feedback(description2), text2)
    
        with self.assertRaises(TypeError):
            TestAppText.app_text._get_description_feedback()
    
    def test_get_last_msg(self):
        text1 = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 90\n\n\nThanks for playing! Please come back soon."
        self.assertEqual(TestAppText.app_text.get_last_msg("win", 90), text1)
        text2 = "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon."
        self.assertEqual(TestAppText.app_text.get_last_msg("lose"), text2)
        text3 = "Thanks for playing! Please come back soon."
        self.assertEqual(TestAppText.app_text.get_last_msg("quit"), text3)
        text4 = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 0\n\n\nThanks for playing! Please come back soon."
        self.assertEqual(TestAppText.app_text.get_last_msg("win", 0), text4)
        
        with self.assertRaises(KeyError):
            TestAppText.app_text.get_last_msg("win")
            TestAppText.app_text.get_last_msg("lose", 90)
            TestAppText.app_text.get_last_msg("qit")

        with self.assertRaises(TypeError):
            TestAppText.app_text.get_last_msg()
    


if __name__ == '__main__':
    unittest.main()