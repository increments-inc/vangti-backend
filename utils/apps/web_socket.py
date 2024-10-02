from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_message_to_channel(request, user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{user.id}-room",
        {
            "type": "send_to_receiver_data",
            'receive_dict': message
        }
    )
    return


def send_message_to_user(user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{user.id}-room",
        {
            "type": "send_to_receiver_data",
            'receive_dict': message
        }
    )
    return


"""
def coin_change_combinations(coins, amount):
    dp = [[] for _ in range(amount + 1)]
    dp[0] = [[]]
    for coin in coins:
        for i in range(coin, amount + 1):
            for combination in dp[i - coin]:
                dp[i].append(combination + [coin])
    return dp[amount]


def coin_change(initial_amount, **kwargs):
    coins = [10, 20, 50, 100, 200, 500, 1000]
    empty_notes = []

    five_hundred = kwargs.get("five_hundred", 0)
    two_hundred = kwargs.get("two_hundred", 0)
    one_hundred = kwargs.get("one_hundred", 0)
    fifty = kwargs.get("fifty", 0)
    twenty = kwargs.get("twenty", 0)
    ten = kwargs.get("ten", 0)

    if five_hundred == two_hundred == one_hundred == fifty == twenty == ten == 0:
        return [x for x in coins if not x >= initial_amount]

    all_combinations = coin_change_combinations(coins, initial_amount)
    logger.info(len(all_combinations))

    sum_note = (
            (five_hundred * 500) +
            (two_hundred * 200) +
            (one_hundred * 100) +
            (fifty * 50) +
            (twenty * 20) +
            (ten * 10)
    )
    if sum_note == initial_amount:
        return []
    remaining_amount = initial_amount-sum_note
    for combin in all_combinations:
        if (
                combin.count(500) >= five_hundred and
                combin.count(200) >= two_hundred and
                combin.count(100) >= one_hundred and
                combin.count(50) >= fifty and
                combin.count(20) >= twenty and
                combin.count(10) >= ten
        ):
            logger.info("here", combin)
            for x in combin:
                empty_notes.append(x)
            # break
    note_list = []
    empty_notes = sorted(list(set(empty_notes)))
    rem_combinations = coin_change_combinations(empty_notes, remaining_amount
                                                )
    for combin in rem_combinations:
        for x in combin:
            note_list.append(x)

    note_list = sorted(list(set(note_list)))

    return note_list
"""
