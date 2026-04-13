from otree.api import *

doc = """
Cycle Network Treatment:
Her grup 3 kişiden oluşur ve sadece komşusuyla etkileşimde bulunur.
"""

class C(BaseConstants):
    NAME_IN_URL = 'network_cycle'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    ENDOWMENT = 15
    BETA = 1.2
    CONVERSION_RATE = 1.0  # 1 token = 1 TL

class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()
        for group in self.get_groups():
            group.assign_cycle_neighbors()
        for p in self.get_players():
            p.degree = 2
            p.network_role = 'member'

class Group(BaseGroup):
    def assign_cycle_neighbors(self):
            players = self.get_players()
            n = len(players)
            if n != C.PLAYERS_PER_GROUP:
                raise ValueError("Cycle network grupları tam olarak 3 kişilik olmalıdır.")

            for i, player in enumerate(players):
                neighbor1 = players[(i + 1) % n]
                neighbor2 = players[(i - 1 + n) % n]
                player.neighbor1_id_in_group = neighbor1.id_in_group
                player.neighbor2_id_in_group = neighbor2.id_in_group

    def set_payoffs(self):
        players = self.get_players()
        contributions = {p.id_in_group: (p.contribution if p.contribution is not None else 0) for p in players}

        for p in players:
            my_contribution = contributions.get(p.id_in_group, 0)

            closed_neighborhood_ids = [
                p.id_in_group,
                p.neighbor1_id_in_group,
                p.neighbor2_id_in_group
                ]
            sum_contributions_in_neighborhood = sum(
                contributions.get(id_in_group, 0) for id_in_group in closed_neighborhood_ids
                )
            neighborhood_size = C.PLAYERS_PER_GROUP
            public_good_return = C.BETA * (sum_contributions_in_neighborhood / neighborhood_size)

            p.payoff = C.ENDOWMENT - my_contribution + public_good_return
    

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

    neighbor1_id_in_group = models.IntegerField()
    neighbor2_id_in_group = models.IntegerField()

    network_role = models.StringField()
    degree = models.IntegerField() 

    consent_given = models.BooleanField(
        label="Yukarıdaki bilgileri okudum ve bu çalışmaya gönüllü olarak katılmayı kabul ediyorum.",
        widget=widgets.CheckboxInput,
        blank=False,
        error_messages={'required': 'Katılım için onay vermeniz gerekiyor'}
    )
    age = models.StringField(label="Yaş aralığınız nedir?", choices=["18–20", "21–23", "24–26", "27–30", "31 ve üzeri"], widget=widgets.RadioSelect)
    gender = models.StringField(label="Cinsiyetiniz nedir?", choices=["Kadın", "Erkek", "Belirtmek istemiyorum", "Diğer"], widget=widgets.RadioSelect)
    field_of_study = models.StringField(label="Okuduğunuz bölüm aşağıdakilerden hangisine daha yakındır?", choices=["Sayısal (STEM)", "Sözel (HASS)", "Karışık / Belirsiz"], widget=widgets.RadioSelect)
    year_of_study = models.StringField(label="Kaçıncı sınıftasınız?", choices=["Hazırlık", "1. sınıf", "2. sınıf", "3. sınıf", "4. sınıf", "Yüksek lisans", "Doktora"], widget=widgets.RadioSelect)
    cgpa = models.StringField(label="Genel not ortalamanız (4 üzerinden):", choices=["0.00–1.99", "2.00–2.49", "2.50–2.99", "3.00–3.49", "3.50–4.00"], widget=widgets.RadioSelect)
    monthly_income = models.StringField(label="Aylık ortalama geliriniz nedir?", choices=["0–1.000 TL", "1.001–3.000 TL", "3.001–5.000 TL", "5.001–10.000 TL", "10.001 TL ve üzeri", "Belirtmek istemiyorum"], widget=widgets.RadioSelect)
    risk_attitude = models.StringField(label="Belirsiz durumlarda risk almayı ne kadar tercih edersiniz?", choices=["Hiç risk almam", "Çok az risk alırım", "Az risk alırım", "Orta düzeyde risk alırım", "Bazen risk alırım", "Sık sık risk alırım", "Risk almayı severim", "Oldukça riskli kararlar alırım", "Neredeyse her zaman risk alırım", "Tam anlamıyla risk severim"], widget=widgets.RadioSelect)


    def get_neighbors(self):
        n1_id = self.field_maybe_none('neighbor1_id_in_group')
        n2_id = self.field_maybe_none('neighbor2_id_in_group')
        if n1_id is None or n2_id is None:
            return [] # Henüz atanmamışsa boş liste döndür
        neighbor1 = self.group.get_player_by_id(n1_id)
        neighbor2 = self.group.get_player_by_id(n2_id)
        return [n for n in [neighbor1, neighbor2] if n is not None]

    # Kapalı komşuluğu getiren fonksiyon (kendisi + komşular)
    def get_closed_neighborhood(self):
        return [self] + self.get_neighbors()


__all__ = ['C', 'Subsession', 'Group', 'Player']