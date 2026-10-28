# star_network/models.py
from otree.api import *

doc = """
Star Network Treatment:
Her grup 3 kişiden oluşur. Bir oyuncu merkez (hub) rolündedir (ID=1) 
ve diğer iki oyuncu (ID=2, ID=3) yalnızca bu merkezle etkileşimde bulunur.
Payofflar kapalı komşuluk bazında hesaplanır.
"""

class C(BaseConstants):
    NAME_IN_URL = 'network_star'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2

    ENDOWMENT_INT = 15
    ENDOWMENT = cu(ENDOWMENT_INT)

    BETA = 1.5
    CONVERSION_RATE = 1.0


class Subsession(BaseSubsession):
    def creating_session(self):
        # Gruplar round1'de rastgele; sonra sabit kalsın
        if self.round_number == 1:
            self.group_randomly()
        else:
            self.group_like_round(1)

        for g in self.get_groups():
            g.assign_star_structure()
            g.build_star_graph_layout()

        for p in self.get_players():
            # Rol ve derece ata
            if p.id_in_group == 1:
                p.network_role = 'center'
                p.degree = 2
            else:
                p.network_role = 'periphery'
                p.degree = 1


class Group(BaseGroup):
    # SVG için her round saklayalım (template’te direkt kullanacağız)
    network_nodes = models.LongStringField(initial='[]')
    network_edges = models.LongStringField(initial='[]')

    def assign_star_structure(self):
        """
        Merkez (ID=1) ve çevre (ID=2, ID=3) komşuluklarını atar.
        """
        if len(self.get_players()) != C.PLAYERS_PER_GROUP:
            raise ValueError("Star network grupları tam olarak 3 kişilik olmalıdır.")

        center = self.get_player_by_id(1)
        periphery1 = self.get_player_by_id(2)
        periphery2 = self.get_player_by_id(3)

        # Center: iki komşu
        center.neighbor1_id = periphery1.id_in_group
        center.neighbor2_id = periphery2.id_in_group

        # Periphery: sadece center komşu
        periphery1.neighbor1_id = center.id_in_group
        periphery1.neighbor2_id = None

        periphery2.neighbor1_id = center.id_in_group
        periphery2.neighbor2_id = None

    def build_star_graph_layout(self):
        """
        Template’te SVG çizimi için basit node/edge koordinatları üretir.
        """
        # 300x300 viewBox
        # Center ortada, çevreler üst/alt gibi
        nodes = [
            dict(id=1, x=150, y=150, role='center'),
            dict(id=2, x=70,  y=90,  role='periphery'),
            dict(id=3, x=70,  y=210, role='periphery'),
        ]
        edges = [
            dict(source=1, target=2),
            dict(source=1, target=3),
        ]

        import json
        self.network_nodes = json.dumps(nodes)
        self.network_edges = json.dumps(edges)

    def set_payoffs(self):
        """
        Payoff = ENDOWMENT - own_contribution + BETA * (sum(contrib in closed neighborhood) / neighborhood_size)
        """
        players = self.get_players()
        contrib = {
            p.id_in_group: (p.contribution if p.contribution is not None else 0)
            for p in players
        }

        for p in players:
            my_c = contrib[p.id_in_group]
            closed_neigh = p.get_closed_neighborhood()
            nsize = len(closed_neigh)
            if nsize <= 0:
                p.payoff = C.ENDOWMENT
                continue

            s = sum(contrib[q.id_in_group] for q in closed_neigh)
            public_return = C.BETA * (s / nsize)

            p.payoff = C.ENDOWMENT - cu(my_c) + cu(public_return)


class Player(BasePlayer):
    # Karar
    contribution = models.IntegerField(min=0, max=C.ENDOWMENT_INT)

    # Komşuluk alanları
    neighbor1_id = models.IntegerField(null=True, blank=True)
    neighbor2_id = models.IntegerField(null=True, blank=True)

    network_role = models.StringField()  # 'center' veya 'periphery'
    degree = models.IntegerField()       # 2 veya 1

    # (Senin projende kullanılan diğer alanları SİLMİYORUM; aşağıda aynen bıraktım)
    consent_given = models.BooleanField(
        label="Yukarıdaki bilgileri okudum ve bu çalışmaya gönüllü olarak katılmayı kabul ediyorum.",
        widget=widgets.CheckboxInput,
        blank=False,
        error_messages={'required': 'Katılım için onay vermeniz gerekiyor'}
    )

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

    # --- Demografi ---
    age = models.StringField(label="Yaş aralığınız nedir?", choices=["18–20", "21–23", "24–26", "27–30", "31 ve üzeri"], widget=widgets.RadioSelect)
    gender = models.StringField(label="Cinsiyetiniz nedir?", choices=["Kadın", "Erkek", "Belirtmek istemiyorum", "Diğer"], widget=widgets.RadioSelect)
    field_of_study = models.StringField(label="Okuduğunuz bölüm aşağıdakilerden hangisine daha yakındır?", choices=["Sayısal (STEM)", "Sözel (HASS)", "Karışık / Belirsiz"], widget=widgets.RadioSelect)
    year_of_study = models.StringField(label="Kaçıncı sınıftasınız?", choices=["Hazırlık", "1. sınıf", "2. sınıf", "3. sınıf", "4. sınıf", "Yüksek lisans", "Doktora"], widget=widgets.RadioSelect)
    cgpa = models.StringField(label="Genel not ortalamanız (4 üzerinden):", choices=["0.00–1.99", "2.00–2.49", "2.50–2.99", "3.00–3.49", "3.50–4.00"], widget=widgets.RadioSelect)
    monthly_income = models.StringField(label="Aylık ortalama geliriniz nedir?", choices=["0–1.000 TL", "1.001–3.000 TL", "3.001–5.000 TL", "5.001–10.000 TL", "10.001 TL ve üzeri", "Belirtmek istemiyorum"], widget=widgets.RadioSelect)
    risk_attitude = models.StringField(label="Belirsiz durumlarda risk almayı ne kadar tercih edersiniz?", choices=[
        "Hiç risk almam", "Çok az risk alırım", "Az risk alırım", "Orta düzeyde risk alırım", "Bazen risk alırım",
        "Sık sık risk alırım", "Risk almayı severim", "Oldukça riskli kararlar alırım", "Neredeyse her zaman risk alırım", "Tam anlamıyla risk severim"
    ], widget=widgets.RadioSelect)

    def get_neighbors(self):
        neighbors = []
        n1 = self.field_maybe_none('neighbor1_id')
        n2 = self.field_maybe_none('neighbor2_id')

        if n1:
            neighbors.append(self.group.get_player_by_id(n1))
        if n2:
            neighbors.append(self.group.get_player_by_id(n2))

        # periphery için neighbor2 zaten None; center için iki komşu gelir
        return [p for p in neighbors if p is not None]

    def get_closed_neighborhood(self):
        return [self] + self.get_neighbors()


__all__ = ['C', 'Subsession', 'Group', 'Player']