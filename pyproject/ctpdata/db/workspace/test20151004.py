import test20151004polymorphism 

class nDuck(test20151004polymorphism.Duck):
## inheritance && init
    def __init__(self):
        test20151004polymorphism.Duck()
        print("inited.")

## redefine
    def quack(self):
        test20151004polymorphism.Duck.quack(self)
        print("nDuck quack")
