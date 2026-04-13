from otree.api import *
from .models import C, Player, Group

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_given']

    def is_displayed(self):
        return self.player.round_number == 1

    def vars_for_template(self):
        return dict(
            participation_bonus=self.session.config.get('participation_fee', 0),
            )

class Instructions(Page):
    def is_displayed(self):
        return self.player.round_number == 1

    def vars_for_template(self):
        group = self.player.group
        group_size = C.PLAYERS_PER_GROUP
        mpcr = group.mpcr
        
# --- ÖRNEKLER       
        ex1_c = 10
        ex1_total_c = ex1_c * group_size
        ex1_keep = C.ENDOWMENT - ex1_c
        ex1_public_return = mpcr * ex1_total_c
        ex1_payoff = ex1_keep + ex1_public_return

        ex2_c = 0
        ex2_total_c = ex2_c * group_size  
        ex2_keep = C.ENDOWMENT - ex2_c
        ex2_public_return = mpcr * ex2_total_c
        ex2_payoff = ex2_keep + ex2_public_return

        ex3_c = 0
        ex3_others_c = 10
        ex3_total_c = (group_size - 1) * ex3_others_c + ex3_c
        ex3_keep = C.ENDOWMENT - ex3_c
        ex3_public_return = mpcr * ex3_total_c
        ex3_payoff = ex3_keep + ex3_public_return

        ex4_c = 10
        ex4_others_c = 0
        ex4_total_c = (group_size - 1) * ex4_others_c + ex4_c
        ex4_keep = C.ENDOWMENT - ex4_c
        ex4_public_return = mpcr * ex4_total_c
        ex4_payoff = ex4_keep + ex4_public_return

        return dict(
            num_rounds=C.NUM_ROUNDS,
            endowment=C.ENDOWMENT,
            participation_bonus=self.session.config.get('participation_fee', 0),
            rate=self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE),
            beta=C.BETA,
            group_size=group_size,
            mpcr_str=f"{mpcr:.2f}",  
            
            ex1_c=ex1_c,
            ex1_total_c=ex1_total_c,
            ex1_keep=ex1_keep,
            ex1_public_return_str=f"{ex1_public_return:.2f}",
            ex1_payoff_str=f"{ex1_payoff:.2f}",
            
            ex2_c=ex2_c,
            ex2_total_c=ex2_total_c,
            ex2_keep=ex2_keep,
            ex2_public_return_str=f"{ex2_public_return:.2f}",
            ex2_payoff_str=f"{ex2_payoff:.2f}",

            ex3_c=ex3_c,
            ex3_others_c=ex3_others_c,
            ex3_total_c_str=f"{ex3_total_c:.2f}",
            ex3_keep=ex3_keep,
            ex3_public_return_str=f"{ex3_public_return:.2f}",
            ex3_payoff_str=f"{ex3_payoff:.2f}",

            ex4_c=ex4_c,
            ex4_others_c=ex4_others_c,
            ex4_total_c_str=f"{ex4_total_c:.2f}",
            ex4_keep=ex4_keep,
            ex4_public_return_str=f"{ex4_public_return:.2f}",
            ex4_payoff_str=f"{ex4_payoff:.2f}",
        )


class Contribution(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        group = self.player.group
        mpcr = group.mpcr
        group_size = C.PLAYERS_PER_GROUP
        other_players_count = group_size - 1

        return dict(
            round_num=self.player.round_number,
            endowment=C.ENDOWMENT,
            beta=C.BETA,
            degree=self.player.degree,
            mpcr=mpcr,
            mpcr_str=f"{mpcr:.2f}",
            group_size=group_size,
            contribution=self.player.field_maybe_none('contribution') or 0,
            other_players_count=other_players_count
        )

class WaitForAll(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.set_payoffs()

    def vars_for_template(player):
        return dict(
            round_num=player.round_number,
            num_rounds=C.NUM_ROUNDS
        )

class Results(Page):
    def vars_for_template(self):
        rate = self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)
        rounds = self.player.in_all_rounds()
        table_cols = []
        cum_payoff = 0
        group_size = C.PLAYERS_PER_GROUP

        for rp in rounds:
            g = rp.group
            your_c = rp.contribution or 0
            total_c = sum(pl.contribution or 0 for pl in g.get_players())
            others_c = total_c - your_c
            mpcr = g.mpcr
            keep = C.ENDOWMENT - your_c
            public_return = mpcr * total_c
            payoff = rp.payoff or 0
            cum_payoff += payoff

            table_cols.append(dict(
                round_num=rp.round_number,
                endowment=C.ENDOWMENT,
                your_contribution=your_c,
                others_contribution=others_c,
                total_contribution=total_c,
                mpcr=mpcr,
                mpcr_str=f"{mpcr:.2f}",  
                keep=keep,
                public_return=public_return,
                public_return_str=str(round(public_return)),  
                payoff=payoff,
                payoff_str=str(round(payoff)),
                payoff_tl=payoff * rate,
                payoff_tl_str=str(round(payoff * rate)),
                cum_payoff=cum_payoff,
                cum_payoff_str=str(round(cum_payoff)),
            ))

        last = table_cols[-1]
        sentence = (
            f"Bu turda ortak havuza {last['your_contribution']} birim verdiniz; "
            f"gruptaki toplam katkı {last['total_contribution']} oldu. "
            f"Toplam katkı MPCR={last['mpcr_str']} ile çarpılarak {round(last['public_return'])} birim olarak dağıtıldı. "
            f"Buna göre bu tur kazancınız {round(last['payoff'])} birim (≈ {round(last['payoff_tl'])} TL)."
        )

        return dict(
            num_rounds=C.NUM_ROUNDS,
            round_num=self.player.round_number,
            rate=rate,
            cols=table_cols,
            this_round_sentence=sentence,
            group_size=group_size,
            beta=C.BETA,
        )
    
class FinalResults(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        rate = self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE)
        participation_bonus = self.session.config.get('participation_fee', 0)
        rounds = self.player.in_all_rounds()
        cols = []
        cum_payoff = 0

        for rp in rounds:
            g = rp.group
            your_c = rp.contribution or 0
            total_c = sum(pl.contribution or 0 for pl in g.get_players())
            mpcr = g.mpcr
            keep = C.ENDOWMENT - your_c
            public_return = mpcr * total_c
            payoff = rp.payoff or 0
            cum_payoff += payoff

            cols.append(dict(
                round_num=rp.round_number,
                your_contribution=your_c,
                total_contribution=total_c,
                mpcr=mpcr,
                mpcr_str=f"{mpcr:.2f}",  
                keep=keep,
                public_return=public_return,
                public_return_str=str(round(public_return)),  
                payoff=payoff,
                payoff_str=str(round(payoff)),
                payoff_tl=payoff * rate,
                payoff_tl_str=str(round(payoff * rate)),
                cum_payoff=cum_payoff,
                cum_payoff_str=str(round(cum_payoff)),
                cum_payoff_tl=cum_payoff * rate,
                cum_payoff_tl_str=str(round(cum_payoff * rate)),
            ))

        total_tokens = cum_payoff
        total_tl_from_game = total_tokens * rate


        grand_total_tl = total_tl_from_game  + participation_bonus

        return dict(
            participant_code=self.participant.code,
            num_rounds=C.NUM_ROUNDS,
            rate=rate,
            endowment=C.ENDOWMENT,
            cols=cols,
            total_tokens=total_tokens,
            total_tl_from_game=total_tl_from_game,
            total_tl_from_game_str=str(round(total_tl_from_game)),
            participation_bonus=participation_bonus,
            participation_bonus_str=str(round(participation_bonus)),
            grand_total_tl=grand_total_tl,
            grand_total_tl_str=str(round(grand_total_tl)),
        )
    
class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'field_of_study',
        'year_of_study',
        'cgpa',
        'monthly_income',
        'risk_attitude',
    ]

    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS
    
    
class AltruismMeasure(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS    
    form_model = 'player'
    form_fields = (
        ['svo_a1', 'svo_a2', 'svo_a3']
        + [f'pt_b{i}' for i in range(1, 11)]
        + ['alt_c1', 'alt_c2']
    )

        
class ThankYou(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS


page_sequence = [
    Consent,
    Instructions,
    Contribution,
    WaitForAll,
    Results,
    FinalResults,
    Demographics,
    AltruismMeasure,
    ThankYou,

]