class Pizza():
    ings = {}
    @classmethod
    def set_ing(cls, value, key):
        cls.ings[value] = key

Pizza.ings['aaa'] = 'bbb'
print(Pizza.ings)
Pizza.set_ing('aaa', 'ccc')
print(Pizza.ings)
Pizza.set_ing('bbb', 'ccc')
print(Pizza.ings)

