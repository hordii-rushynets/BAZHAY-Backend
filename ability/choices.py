currency_choices = [
        ('UAH', 'UAH'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('PLN', 'PLN'),
        ('GBP', 'GBP'),
        ('CAD', 'CAD'),
        ('NOK', 'NOK'),
        ('CHF', 'CHF'),
        ('SEK', 'SEK'),
]

access_type_choices = [
        ('subscribers', 'Subscribers'),
        ('everyone', 'Everyone'),
        ('only_me', 'Only_me'),
]

access_type_list = [_[0] for _ in access_type_choices]

valid_mime_types = ['video/mp4', 'video/avi', 'video/mov', 'video/mpeg']
