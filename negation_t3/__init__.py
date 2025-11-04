from otree.api import *
import random
import json
import math



doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'negation_t3'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 6
    COST = 4
    INVALID_REWARD = 0
    SHOW_UP_FEE = 7
    ENDOWMENT = COST * 10
    CONVERSION_RATE = 4


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    valid_no = models.IntegerField()
    valid_actions = models.StringField()
    invalid_actions = models.StringField()
    possible_rewards = models.StringField()
    message = models.StringField(blank=True)
    message_cost = models.IntegerField()
    action = models.StringField(blank=True)
    reward = models.IntegerField()
    receiver_actions = models.StringField()
    sender_actions = models.StringField()

class Player(BasePlayer):
    q1 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q2 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q3 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q4 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q5 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    q6 = models.IntegerField(choices=[[1, 'True'], [0, 'False']], widget=widgets.RadioSelect, label='')
    play_round_number = models.IntegerField(initial=0)
    type = models.StringField()
    prob_5 = models.FloatField()
    prob_align_actions = models.FloatField()

# functions
def creating_session(subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
    else:
        subsession.group_like_round(1)
    for i in subsession.get_players():
        i.prob_5 = round(subsession.session.config['prob_5'],2)
        i.prob_align_actions = subsession.session.config['prob_align_action']
        if i.id_in_group == 1:
            i.type = "Sender"
        else:
            i.type = "Receiver"
        if i.round_number >= 2:
            i.play_round_number = i.round_number - 1


# PAGES
class Instructions(Page):
    form_model = "player"
    form_fields = ["q1", "q2", "q3", "q4", "q5", "q6"]

    @staticmethod
    def error_message(player, values):
        solutions = dict(q1=1,
                         q2=1,
                         q3=1,
                         q4=0,
                         q5=0,
                         q6=0)
        error_messages = dict()
        for field_name in solutions:
            if values[field_name] != solutions[field_name]:
                error_messages[field_name] = 'Wrong answer'
        return error_messages

    def is_displayed(player: Player):
        return player.round_number == 1

    def vars_for_template(player: Player):
        return dict(
            possible_rewards = random.sample([40,50,60,70,80,90,100], 7),
            num_playrounds = C.NUM_ROUNDS - 1,
            num_players = player.session.num_participants,
            num_groups = int(player.session.num_participants/2),
            prob_2=1 - player.prob_5,
            prob_not_align = round(1-player.prob_align_actions,2)
        )

class StartWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group:Group):
        player = group.get_players()
        letters = ['A','B','C','D','E','F','G','H','J','K','L','M']
        rewards = [40,50,60,70,80,90,100]
        random_rewards = random.sample(rewards, 7)
        group.possible_rewards = json.dumps(random_rewards)
        receiver_actions = random.sample(letters, 7)
        group.receiver_actions = json.dumps(sorted(receiver_actions))
        if random.random() < player[0].prob_5:
            group.valid_no=5
        else:
            group.valid_no = 2
        valid = random.sample(receiver_actions, group.valid_no)
        valid_sorted = sorted(valid)
        group.valid_actions = json.dumps(valid_sorted)
        if random.random() < player[0].prob_align_actions:
            group.sender_actions = group.receiver_actions
        else:
            remaining = list(set(letters) - set(valid))
            extra = random.sample(remaining, 7 - group.valid_no)
            group.sender_actions = json.dumps(sorted(json.loads(group.valid_actions) + extra))
        invalid = sorted(set(json.loads(group.sender_actions)) - set(valid))
        group.invalid_actions = json.dumps(invalid)

class Sender(Page):
    form_model = "group"
    form_fields = ["message"]

    def vars_for_template(player: Player):
        group = player.group
        return dict(
            sender_actions = ", ".join(json.loads(group.sender_actions)),
            valid_actions = json.loads(group.valid_actions),
            invalid_actions = json.loads(group.invalid_actions),
            prob_2 = 1-player.prob_5
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.type == "Sender"

class ReceiverWaitPage(WaitPage):
    body_text = "Waiting for the Sender's message."

    def is_displayed(player: Player):
        return player.type == "Receiver"

class Receiver(Page):
    form_model = "group"
    form_fields = ["action"]

    def vars_for_template(player: Player):
        group = player.group
        action_reward_pairs = list(zip(json.loads(group.receiver_actions), json.loads(group.possible_rewards)))
        return dict(
            receiver_actions=" , ".join(json.loads(group.receiver_actions)),
            action_reward_pairs = action_reward_pairs,
            prob_2=1 - player.prob_5
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.type == "Receiver"


class ResultsWaitPage(WaitPage):
    body_text = "Waiting for the Receiver's action."

    @staticmethod
    def after_all_players_arrive(group: Group):
        player_list = group.get_players()
        group.message_cost = max(0, len(group.message)-1) * C.COST
        index = json.loads(group.receiver_actions).index(group.action)
        if group.action in json.loads(group.valid_actions):
            group.reward = json.loads(group.possible_rewards)[index]
        else:
            group.reward = C.INVALID_REWARD
        for player in player_list:
            player.payoff = C.ENDOWMENT + group.reward - group.message_cost


class Results(Page):
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            participant = player.participant
            selected_rounds = random.sample(range(2, C.NUM_ROUNDS + 1), 2)
            participant.selected_rounds = [selected_rounds[0]-1, selected_rounds[1]-1]
            p1 = player.in_round(selected_rounds[0]).payoff
            p2 = player.in_round(selected_rounds[1]).payoff
            participant.selected_payoffs = [p1, p2]
            participant.highest_payoff = max(p1, p2)
            participant.payoff = math.ceil(participant.highest_payoff/C.CONVERSION_RATE + C.SHOW_UP_FEE)

    def vars_for_template(player: Player):
        group = player.group
        action_reward_pairs = list(zip(json.loads(group.receiver_actions), json.loads(group.possible_rewards)))
        return dict(
            sender_actions=", ".join(json.loads(group.sender_actions)),
            receiver_actions=" , ".join(json.loads(group.receiver_actions)),
            valid_actions = json.loads(group.valid_actions),
            valid_actions_string = ", ".join(json.loads(group.valid_actions)),
            invalid_actions=json.loads(group.invalid_actions),
            possible_rewards=json.loads(group.possible_rewards),
            action_reward_pairs=action_reward_pairs,
            prob_2=1 - player.prob_5
        )

class AllGroupsWaitPage(WaitPage):
    wait_for_all_groups = True
    body_text = "Waiting for all participants to finish this round."

class FinalPayoff(Page):
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        selected_rounds = player.participant.vars.get("selected_rounds", [])

        rounds_data = []
        for p in player.in_all_rounds():
            if p.round_number > 1:
                rounds_data.append({
                    'round_number': p.round_number-1,
                    'payoff': int(p.payoff),  # removes decimals if you’re using integer points
                    'is_selected': p.round_number - 1 in selected_rounds
                })
        return dict(
            rounds_data=rounds_data,
            max_round_payoff = player.participant.payoff - C.SHOW_UP_FEE
        )


page_sequence = [Instructions, StartWaitPage, Sender, ReceiverWaitPage, Receiver, ResultsWaitPage, Results, AllGroupsWaitPage, FinalPayoff]
