SESSION_CONFIGS = [
    dict(
        name='network_control',
        display_name="Control Topology",
        num_demo_participants=3,
        app_sequence=['network_control'],
    ),
    dict(
        name='network_cycle',
        display_name="Cycle Topology",
        num_demo_participants=24,
        app_sequence=['network_cycle'],
    ),
    dict(
        name='network_star',
        display_name="Star Topology",
        num_demo_participants=24,
        app_sequence=['network_star'],
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.0,
    participation_fee=100.0,
    doc="",
)

LANGUAGE_CODE = 'tr'
REAL_WORLD_CURRENCY_CODE = 'TRY'
USE_POINTS = True

INSTALLED_APPS = ['otree', 'network_control', 'network_cycle', 'network_star']

SECRET_KEY = 'eoy'
ADMIN_USERNAME = 'eoy'
ADMIN_PASSWORD = 'eoy'