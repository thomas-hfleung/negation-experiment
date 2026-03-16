from otree.api import *

import math


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'payment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PRACTICE_ROUNDS = 3



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class FinalPayoff(Page):

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant

        comm = participant.vars.get('comm_payoff', 0)
        bret = participant.vars.get('bret_payoff', 0)
        showup = int(player.session.config['participation_fee'])
        rounds_data = participant.vars.get('rounds_data', [])

        total = math.ceil(comm + bret + showup)

        participant.payoff = total

        return dict(
            comm_payoff=comm,
            bret_payoff=bret,
            showup_fee=showup,
            total_payoff=total,
            conversion_rate=player.session.config['conversion_rate'],
            rounds_data=rounds_data,
        )


page_sequence = [FinalPayoff]
