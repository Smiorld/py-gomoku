from threading import Timer

def hello(a):
    print(a)

t = Timer(3, hello, ['hello'])
t.start()
t.cancel()
t=Timer(1, hello, ['yeah'])
t.start()