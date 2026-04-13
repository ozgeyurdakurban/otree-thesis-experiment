from otree.api import *

doc = """
Control Treatment:
Her grup 24 kişiden oluşur ve oyuncuların hepsi birbiriyle etkileşimde bulunur.
"""

class C(BaseConstants):
    NAME_IN_URL = 'network_control'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    ENDOWMENT = 15
    BETA = 1.2
    CONVERSION_RATE = 1.0  # 1 token = 1 TL

class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()
        for p in self.get_players():
            p.degree = C.PLAYERS_PER_GROUP
            p.network_role = 'member'

class Group(BaseGroup):
    @property
    def mpcr(self):
        return C.BETA / C.PLAYERS_PER_GROUP

    def set_payoffs(self):
        players = self.get_players()
        total_contribution = sum(p.contribution for p in players)
        for p in players:
            p.payoff = C.ENDOWMENT - p.contribution + self.mpcr * total_contribution

class Player(BasePlayer):
    # Alturism ölçümleri
    # --- Section A: SVO (A/B/C) ---
    svo_a1 = models.StringField(choices=['A', 'B', 'C'])
    svo_a2 = models.StringField(choices=['A', 'B', 'C'])
    svo_a3 = models.StringField(choices=['A', 'B', 'C'])

    # --- Section B: Likert 1..7 ---
    pt_b1  = models.IntegerField(choices=range(1, 8))
    pt_b2  = models.IntegerField(choices=range(1, 8))
    pt_b3  = models.IntegerField(choices=range(1, 8))
    pt_b4  = models.IntegerField(choices=range(1, 8))
    pt_b5  = models.IntegerField(choices=range(1, 8))
    pt_b6  = models.IntegerField(choices=range(1, 8))
    pt_b7  = models.IntegerField(choices=range(1, 8))
    pt_b8  = models.IntegerField(choices=range(1, 8))
    pt_b9  = models.IntegerField(choices=range(1, 8))
    pt_b10 = models.IntegerField(choices=range(1, 8))

    # --- Section C: sliders 0..10 ---
    alt_c1 = models.IntegerField(min=0, max=10)
    alt_c2 = models.IntegerField(min=0, max=10)

    # Deney alanları
    contribution = models.IntegerField(min=0, max=C.ENDOWMENT)

    network_role = models.StringField()
    degree = models.IntegerField()

    consent_given = models.BooleanField(
        label="Yukarıdaki bilgileri okudum ve bu çalışmaya gönüllü olarak katılmayı kabul ediyorum.",
        widget=widgets.CheckboxInput,
        blank=False,
        error_messages={'required': 'Katılım için onay vermeniz gerekiyor'}
    )


    age = models.StringField(
        label="Yaş aralığınız nedir?",
        choices=["18–20", "21–23", "24–26", "27–30", "31 ve üzeri"],
        widget=widgets.RadioSelect
    )

    gender = models.StringField(
        label="Cinsiyetiniz nedir?",
        choices=["Kadın", "Erkek", "Belirtmek istemiyorum", "Diğer"],
        widget=widgets.RadioSelect
    )

    field_of_study = models.StringField(
        label="Okuduğunuz bölüm aşağıdakilerden hangisine daha yakındır?",
        choices=["Sayısal (STEM)", "Sözel (HASS)", "Karışık / Belirsiz"],
        widget=widgets.RadioSelect
    )

    year_of_study = models.StringField(
        label="Kaçıncı sınıftasınız?",
        choices=["Hazırlık", "1. sınıf", "2. sınıf", "3. sınıf", "4. sınıf", "Yüksek lisans", "Doktora"],
        widget=widgets.RadioSelect
    )

    cgpa = models.StringField(
        label="Genel not ortalamanız (4 üzerinden):",
        choices=["0.00–1.99", "2.00–2.49", "2.50–2.99", "3.00–3.49", "3.50–4.00"],
        widget=widgets.RadioSelect
    )

    monthly_income = models.StringField(
        label="Aylık ortalama geliriniz nedir?",
        choices=["0–1.000 TL", "1.001–3.000 TL", "3.001–5.000 TL", "5.001–10.000 TL", "10.001 TL ve üzeri", "Belirtmek istemiyorum"],
        widget=widgets.RadioSelect
    )

    risk_attitude = models.StringField(
        label="Belirsiz durumlarda risk almayı ne kadar tercih edersiniz?",
        choices=[
            "Hiç risk almam", "Çok az risk alırım", "Az risk alırım", "Orta düzeyde risk alırım",
            "Bazen risk alırım", "Sık sık risk alırım", "Risk almayı severim",
            "Oldukça riskli kararlar alırım", "Neredeyse her zaman risk alırım", "Tam anlamıyla risk severim"
        ],
        widget=widgets.RadioSelect
    )

__all__ = ['C', 'Subsession', 'Group', 'Player']