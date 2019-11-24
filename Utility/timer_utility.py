from threading import Timer
from time import sleep
from Utility import is_member

import time


def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator


# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:

        #print( "Elapsed time: %f seconds.\n" %tempTimeInterval )
        return tempTimeInterval


def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)


class RepeatedTimer(object):

    def __init__(self, interval= 1, start_function=None, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.timer_function = start_function
        self._stop_function = None
        self.is_running = False
        self.limit = 10

        self.__start_input_args = args
        self.__start_input_kwargs = kwargs
        self.__stop_input_args = ()
        self.__stop_input_kwargs = {}
        self._start_time = 0

    @property
    def stop_function(self)->callable:
        return self._stop_function

    @stop_function.setter
    def stop_function(self, stop_function: callable):
        if callable(stop_function):
            self._stop_function = stop_function

    @property
    def start_input_args(self)->tuple:
        return self.__start_input_args

    @start_input_args.setter
    def start_input_args(self,args: tuple):
        self.__start_input_args = args

    @property
    def start_input_kwargs(self):
        return self.__start_input_kwargs

    @start_input_kwargs.setter
    def start_input_kwargs(self,kwargs):
        self.__start_input_kwargs = kwargs

    @property
    def stop_input_args(self:tuple)->tuple:
        return self.__stop_input_args

    @stop_input_args.setter
    def stop_input_args(self, args: tuple):
        self.__stop_input_args = args

    @property
    def stop_input_kwargs(self):
        return self.__stop_input_kwargs

    @stop_input_kwargs.setter
    def stop_input_kwargs(self, kwargs):
        self.__start_input_kwargs = kwargs


    def set_attr(self, **kwargs):

        default = ['interval', 'timer_function', 'start_input_args', 'start_input_kwargs',
                   'stop_function', 'stop_input_args', 'stop_input_kwargs', 'limit']
        fileds = list(kwargs.keys())
        (state, missing) = is_member(fileds, default)

        assert state, 'thar is no such member :' + missing
        # setup = default.copy()
        # setup.update(prop)
        for name in kwargs.keys():
            self.__setattr__(name, kwargs[name])

    def _run(self):

        self.is_running = False
        self.start()
        self.timer_function(*self.__start_input_args, **self.__start_input_kwargs)
        self._start_time += toc()
        if self.limit <= self._start_time:
            self.stop()

    def start(self):

        if not self.is_running:

            self._timer = Timer(self.interval, self._run)

            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
        self._start_time = 0
        if callable(self._stop_function):
            self._stop_function(* self.__stop_input_args, ** self.__stop_input_kwargs)


def hello(name):
    print("Hello %s!" % name)


def main():
    print("starting...")
    rt = RepeatedTimer(1, lambda x: hello(x))
    rt.start_input_args = ['world']

    try:
        rt.start()
         # your long-running job goes here...
        sleep(5)
    finally:
        hello('finis')
        rt.stop()  # better in a try/finally block to make sure the program ends!


if __name__ == "__main__":
    main()
