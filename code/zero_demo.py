from keras.layers import Activation, BatchNormalization
from keras.layers import Conv2D, Dense, Flatten, Input
from keras.models import Model
from dlgo import scoring
from dlgo import zero
from dlgo.goboard import GameState, Player, Point

# tag::zero_simulate[]
def simulate_game(
        board_size,
        black_agent, black_collector,
        white_agent, white_collector):
    print('Starting the game!')
    game = GameState.new_game(board_size)
    agents = {
        Player.black: black_agent,
        Player.white: white_agent,
    }

    black_collector.begin_episode()
    white_collector.begin_episode()
    while not game.is_over():
        next_move = agents[game.next_player].select_move(game)
        game = game.apply_move(next_move)

    game_result = scoring.compute_game_result(game)
    if game_result.winner == Player.black:
        black_collector.complete_episode(1)
        white_collector.complete_episode(-1)
    else:
        black_collector.complete_episode(-1)
        white_collector.complete_episode(1)
# end::zero_simulate[]


# tag::zero_model[]
board_size = 9
encoder = zero.ZeroEncoder(board_size)

board_input = Input(shape=encoder.shape(), name='board_input')
pb = board_input
for i in range(4):                     # <1>
    pb = Conv2D(64, (3, 3),            # <1>
        padding='same',                # <1>
        data_format='channels_first',  # <1>
        activation='relu')(pb)         # <1>

policy_conv = \                                         # <2>
    Conv2D(2, (1, 1),                                   # <2>
        data_format='channels_first',                   # <2>
        activation='relu')(pb)                          # <2>
policy_flat = Flatten()(policy_conv)                    # <2>
policy_output = \                                       # <2>
    Dense(encoder.num_moves(), activation='softmax')(   # <2>
        policy_flat)                                    # <2>

value_conv = \                                           # <3>
    Conv2D(1, (1, 1),                                    # <3>
        data_format='channels_first',                    # <3>
        activation='relu')(pb)                           # <3>
value_flat = Flatten()(value_conv)                       # <3>
value_hidden = Dense(256, activation='relu')(value_flat) # <3>
value_output = Dense(1, activation='tanh')(value_hidden) # <3>

model = Model(
    inputs=[board_input],
    outputs=[policy_output, value_output])
# end::zero_model[]

# tag::zero_train[]
black_agent = zero.ZeroAgent(
    model, encoder, rounds_per_move=10, c=2.0)  # <4>
white_agent = zero.ZeroAgent(
    model, encoder, rounds_per_move=10, c=2.0)
c1 = zero.ZeroExperienceCollector()
c2 = zero.ZeroExperienceCollector()
black_agent.set_collector(c1)
white_agent.set_collector(c2)

for i in range(5):   # <5>
    simulate_game(board_size, black_agent, c1, white_agent, c2)

exp = zero.combine_experience([c1, c2])
black_agent.train(exp, 0.01, 2048)
# end::zero_train[]
