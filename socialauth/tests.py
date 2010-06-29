from selenium import selenium
import unittest
from django.contrib.auth.models import User

from test_data import *

class TwitterTester(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", test_base_url)
        self.selenium.start()
    
    def testTwitter(self):
        sel = self.selenium
        #Test that a user is created after logging in via Twitter for the first time.
        initial_user_count = User.objects.count()
        sel.open("/accounts/login/")
        sel.click("link=Login via twitter")
        sel.wait_for_page_to_load("30000")
        try:
            sel.click("link=Sign out")
            sel.wait_for_page_to_load("30000")
        except:
            pass
        sel.type("username_or_email", twitter_username)
        sel.type("session[password]", twitter_password)
        sel.click("allow")
        sel.wait_for_page_to_load("30000")
        sel.open("/accounts/login/")
        sel.open("/accounts/edit/profile/")
        self.assertEqual(initial_user_count + 1, User.objects.count())
        
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
        

class OpenIdTester(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", test_base_url)
        self.selenium.start()
    
    def testOpenId(self):
        initial_user_count = User.objects.count()
        sel = self.selenium
        sel.open("/accounts/login/")
        sel.click("openid_login_link")
        sel.wait_for_page_to_load("30000")
        sel.type("openid_url", myopenid_url)
        sel.click("//input[@value='Sign in']")
        sel.wait_for_page_to_load("30000")
        try:
            sel.type("password", myopenid_password)
            sel.click("signin_button")
            sel.wait_for_page_to_load("30000")
        except:
            sel.click("continue-button")
        sel.wait_for_page_to_load("30000")
        sel.open("/accounts/login/")
        self.assertEqual(initial_user_count + 1, User.objects.count())
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()



if __name__ == "__main__":
    unittest.main()
