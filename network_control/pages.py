from otree.api import *
from .models import C, Player, Group

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_given']

    def is_displayed(self):
        return self.player.round_number == 1

    def vars_for_template(self):
        group = self.player.group
        mpcr = group.mpcr
        return dict(
            num_rounds=C.NUM_ROUNDS,
            endowment=C.ENDOWMENT,
            beta=C.BETA,
            group_size=C.PLAYERS_PER_GROUP,
            mpcr_str=f"{mpcr:.3f}",
            participation_bonus=self.session.config.get('participation_fee', 0),
            rate=self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE),
        )

class Instructions(Page):
    def is_displayed(self):
        return self.player.round_number == 1

    def vars_for_template(self):
        group = self.player.group
        example_contribution = 10
        group_size = C.PLAYERS_PER_GROUP
        total_contribution = example_contribution * group_size
        mpcr = group.mpcr
        example_payoff = (C.ENDOWMENT - example_contribution) + mpcr * total_contribution

        return dict(
            num_rounds=C.NUM_ROUNDS,
            endowment=C.ENDOWMENT,
            participation_bonus=self.session.config.get('participation_fee', 0),
            rate=self.session.config.get('real_world_currency_per_point', C.CONVERSION_RATE),
            beta=C.BETA,
            group_size=group_size,
            mpcr_str=f"{mpcr:.3f}",
            example_contribution=example_contribution,
            total_contribution=total_contribution,
            example_payoff_str=f"{example_payoff:.3f}",
        )

class AltruismMeasure(Page):
    form_model = 'player'
    form_fields = ['dg_amount', 'svo_importance']

    def is_displayed(self):
        return self.player.round_number == 1

    def vars_for_template(self):
        dg = self.player.field_maybe_none('dg_amount') or 0
        svo = self.player.field_maybe_none('svo_importance') or 5
        dg_keep = 100 - dg

        return dict(dg=dg, svo=svo, dg_keep=dg_keep)

    def error_message(self, values):
        errors = []
        dg = values.get('dg_amount')
        svo = values.get('svo_importance')

        if dg is None or not (0 <= dg <= 100):
            errors.append('Lütfen 0 ile 100 TL arasında bir miktar seçiniz.')
        elif dg % 10 != 0:
            errors.append('Lütfen yalnızca 10’un katı olan bir miktar giriniz (örn. 0, 10, 20, ..., 100).')

        if svo is None or not (0 <= svo <= 10):
            errors.append('Lütfen 0 ile 10 arasında bir değer seçiniz.')

        if errors:
            return ' '.join(errors)

class Contribution(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        group = self.player.group
        mpcr = group.mpcr
        return dict(
            round_num=self.player.round_number,
            endowment=C.ENDOWMENT,
            beta=C.BETA,
            degree=self.player.degree,
            mpcr=mpcr,
            mpcr_str=f"{mpcr:.3f}",
            group_size=C.PLAYERS_PER_GROUP,
            contribution=self.player.field_maybe_none('contribution') or 0
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
                mpcr_str=f"{mpcr:.3f}",  
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
                mpcr_str=f"{mpcr:.3f}",  
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

        try:
            dg_given = self.player.in_round(1).dg_amount or 0
        except Exception:
            dg_given = 0
        retained_amount = 100 - dg_given
        grand_total_tl = total_tl_from_game + retained_amount + participation_bonus

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
            retained_amount=retained_amount,
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
    
class ThankYou(Page):
    def is_displayed(self):
        return self.player.round_number == C.NUM_ROUNDS


page_sequence = [
    Consent,
    Instructions,
    AltruismMeasure,
    Contribution,
    WaitForAll,
    Results,
    FinalResults,
    Demographics,
    ThankYou,
]