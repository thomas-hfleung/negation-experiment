from os import environ

SESSION_CONFIGS = [
    dict(
        name='Negation_baseline',
        app_sequence=['negation_app'],
        num_demo_participants=2,
        prob_5=0.5,
    ),
    dict(
        name='Negation_t1',
        app_sequence=['negation_app'],
        num_demo_participants=2,
        prob_5=0.3,
    ),
    dict(
        name='Negation_t2',
        app_sequence=['negation_app'],
        num_demo_participants=2,
        prob_5=0.7,
    ),
    dict(
        name='Negation_t3',
        app_sequence=['negation_t3'],
        num_demo_participants=2,
        prob_5=0.5,
        prob_align_action = 0.8,
    ),
    dict(
        name='BRET',
        app_sequence=['bret'],
        num_demo_participants=1,
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ["selected_rounds", "highround", "selected_payoffs", "highest_payoff"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = ''
USE_POINTS = False
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 0

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '9542391672666'

DEBUG = False
