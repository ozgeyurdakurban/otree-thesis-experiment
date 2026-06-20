# =========================================================
# SESSION CONFIGURATIONS
# Her session config, oTree admin panelinde ayrı bir oturum
# türü olarak görünür.
# =========================================================

SESSION_CONFIGS = [

    # -----------------------------------------------------
    # Tek başına Control treatment'ını çalıştırmak için
    # -----------------------------------------------------
    dict(
        name='network_control',
        display_name="Control Treatment",
        num_demo_participants=3,
        app_sequence=['network_control'],
    ),

    # -----------------------------------------------------
    # Tek başına Cycle treatment'ını çalıştırmak için
    # -----------------------------------------------------
    dict(
        name='network_cycle',
        display_name="Cycle Treatment",
        num_demo_participants=3,
        app_sequence=['network_cycle'],
    ),

    # -----------------------------------------------------
    # Tek başına Star treatment'ını çalıştırmak için
    # -----------------------------------------------------
    dict(
        name='network_star',
        display_name="Star Treatment",
        num_demo_participants=3,
        app_sequence=['network_star'],
    ),

    # -----------------------------------------------------
    # Tüm blokların tek uygulama içinde yürütüldüğü ana yapı
    # block_order sabit verilirse treatment sırası random olmaz
    # -----------------------------------------------------
    dict(
        name='network_within',
        app_sequence=['network_within'],
        num_demo_participants=3,
        participation_fee=100,
        real_world_currency_per_point=1.0,
    #    block_order=['control', 'cycle', 'star'],
    ),
]


# =========================================================
# DEFAULT SESSION SETTINGS
# Buradaki değerler, SESSION_CONFIGS içinde ayrıca
# tanımlanmadığı sürece varsayılan olarak kullanılır.
# =========================================================

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.0,
    participation_fee=100.0,
    doc="",
)


# =========================================================
# LANGUAGE AND CURRENCY SETTINGS
# =========================================================

LANGUAGE_CODE = 'tr'
REAL_WORLD_CURRENCY_CODE = 'TRY'
USE_POINTS = True


# =========================================================
# INSTALLED APPS
# oTree'nin ve projedeki uygulamaların burada tanımlanması gerekir
# =========================================================

INSTALLED_APPS = [
    'otree',
    'network_within',
    'network_control',
    'network_cycle',
    'network_star',
]


# =========================================================
# ADMIN AND SECURITY SETTINGS
# Not: Bu bilgileri GitHub'a koymadan önce mutlaka değiştir.
# Özellikle gerçek bir sunucuya çıkarken güçlü bir admin şifresi kullan.
# =========================================================

SECRET_KEY = 'eoy'
ADMIN_USERNAME = 'eoy'
ADMIN_PASSWORD = 'eoy'