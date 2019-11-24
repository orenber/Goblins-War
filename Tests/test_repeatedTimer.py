from unittest import TestCase
from Utility.timer_utility import RepeatedTimer


class TestRepeatedTimer(TestCase):
    def setUp(self):
        self.timer = RepeatedTimer()
        self.time_fun = lambda x:hello(x)

    def test_start_input_args(self):

        time_fun = lambda x:print(x)
        self.timer = RepeatedTimer(1,time_fun,5,6)
        constructor_intearface =  self.timer.start_input_args
        self.timer.start_input_args = 5,6
        seting_input  = self.timer.start_input_args
        self.assertEqual(constructor_intearface,seting_input)


    def test_set_attr(self):

        self.timer.set_attr(timer_function=self.time_fun, interval= 1, start_input_args = ['test_set_attr'],limit=10)

        self.timer.start()

    def test_start(self):

        self.timer.set_attr( timer_function = self.time_fun, interval=1 )
        self.timer.start_input_args = ['test_start']
        self.timer.start()

    def test_stop(self):

        self.timer.set_attr(timer_function=self.time_fun, stop_function=self.time_fun, interval= 0.01, limit=0.05)
        self.timer.start_input_args = ['test_stop']
        self.timer.stop_input_args = ['stop']
        self.timer.start()


def hello(name):
    print("Hello %s!" % name)