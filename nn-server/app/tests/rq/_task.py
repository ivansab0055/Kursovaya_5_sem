import time


def example(seconds: int = 15):
    for i in range(seconds):
        print(i)
        time.sleep(1)
