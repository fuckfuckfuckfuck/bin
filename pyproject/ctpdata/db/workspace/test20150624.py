## Multiple inheritance peoblem

class A(object):
    def __init__(self):
        self.some_name = 'A'

    def print_a(self):
        print self.some_name

class B(object):
    def __init__(self):
        self.some_name = 'B'

    def print_b(self):
        print self.some_name

class C(A, B):
    def __init__(self):
        A.__init__(self)
        B.__init__(self)

# if __name__ == '__main__':
#     c = C()
#     c.print_a()


# (1) You only have a single object here; the some_name property is shared between methods from all inherited classes. You call A.__init__, which sets it to A, then B.__init__, which changes it to B.
# Also note that you're calling base methods incorrectly; use super:

# (2) There's only one self, and you're overwriting its some_name in B.__init__. Maybe you're used to C++, where there would be two separate fields, A.some_name and B.some_name. This concept doesn't apply to Python, where attributes are created dynamically on assignment.
 
class AA(object):
    def __init__(self):
        self.some_name = 'AA'
        print('AA')
        super(AA, self).__init__()

    def print_a(self):
        print self.some_name

class BB(object):
    def __init__(self):
        self.some_name = 'BB'
        print('BB')
        super(BB, self).__init__()

    def print_b(self):
        print self.some_name

class CC(AA, BB):
    def __init__(self):
        super(CC, self).__init__()

if __name__ == '__main__':
    c = C()
    c.print_a()
    cc = CC()
    cc.print_a()

