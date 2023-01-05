from utils import get_suit, get_min_max_cards, get_suit_cards, CARDS_DICT, get_partner_idx, pick_winning_card_idx, is_high, index, find


def get_bid(body):
    MIN_BID = 16
    PASS_BID = 0

    own_cards = body["cards"]

    # Considering J and 9 as strong cards
    strong_cards = {'J':0, '9':0}
    for idx in range(len(own_cards)):
        card = own_cards[idx][0]
        if card in strong_cards:
            if card == 'J':
                strong_cards[card] += 3
            else:
                strong_cards[card] += 2

    strong_cards_sum = sum(strong_cards.values())
    # print("\n\nStrong cards", strong_cards)

    bid_history = body["bidHistory"]
    # when you are the first player to bid, use the minimum bid
    if len(bid_history) == 0:
        return {"bid": MIN_BID}

    # Determining the last bid?
    bid_list = []
    for i in bid_history:
        bid_list.append(i[1])
    last_max_bid = max(bid_list)
    # print("\n\n Last Bid1", last_max_bid)

    # when you have two or more J or 9, go to a higher bid
    # if the bid is already 18, pass
    if(strong_cards_sum >= 5 and last_max_bid != 0):
        if(strong_cards["J"]/3 <= 1 and last_max_bid < 17):
            return {"bid": last_max_bid+1}
        elif(strong_cards["J"]/3 > 1 and last_max_bid < 19):
            return {"bid": last_max_bid+1}
        else:
            return {"bid": PASS_BID}
    else:
        return {"bid": PASS_BID}
        

    # For choose_trump_suit testing purposes
    # if last_bid < 20:
    #     return{"bid": last_bid + 1}
    # else:
    #     return{"bid": PASS_BID}

def get_trump_suit(body):

    # get the suit with the highest count
    own_cards = body["cards"]
    own_card_suits = []
    for card in own_cards:
        own_card_suits.append(get_suit(card))

    possible_suits = {'H':0, 'S':0, 'C':0, 'D':0}
    for suit in own_card_suits:
        possible_suits[suit] += 1
    
    print(possible_suits)
    trump_suit = max(possible_suits, key=possible_suits.get)
    return {"suit": trump_suit}


def get_play_card(body):
    own_cards = body["cards"]
    first_card = None if len(body["played"]) == 0 else body["played"][0]
    trump_suit = body["trumpSuit"]
    trump_revealed = body["trumpRevealed"]
    hand_history = body["handsHistory"]
    own_id = body["playerId"]
    played = body["played"]
    player_ids = body["playerIds"]
    my_idx = player_ids.index(own_id)
    my_idx = index(
        player_ids, lambda id: id == own_id)
    my_partner_idx = get_partner_idx(my_idx)
    first_turn = (my_idx + 4 - len(played)) % 4
    is_bidder = trump_suit and not trump_revealed


    # Getting min and max cards 
    _, max_own_card, _ = get_min_max_cards(own_cards)
 
    # if we are the one to throw the first card in the hands, throw the highest card
    if (not first_card):
        return{"card": max_own_card}
    
    first_card_suit = get_suit(first_card)
    own_suit_cards = get_suit_cards(own_cards, first_card_suit)

    # if we have the suit with respect to the first card, we throw it
    if len(own_suit_cards) > 0:
        own_suit_card_dict, max_own_suit_card, min_own_suit_card = get_min_max_cards(own_suit_cards)
        played_card_dict, max_played_card, _ = get_min_max_cards(played)

        played_suits = [get_suit(card) for card in played]
        has_trump = True if trump_suit in played_suits else False
        print("\n\n", max_own_suit_card, max_played_card, min_own_suit_card)

        # If your partner has thrown the highest card, increase points by throwing your highest
        if(not has_trump):
            if(len(played) > 1):
                print("\n\n Partner's card", list(played_card_dict.keys())[len(played) - 2])
                if(max_played_card == list(played_card_dict.keys())[len(played) - 2]):
                    return{"card":max_own_suit_card}
        
        # We throw the highest one if we have one higher than highest played card
        # Else we throw the lowest card
        # print("\n\n", has_trump)
        if (played_card_dict[max_played_card] > own_suit_card_dict[max_own_suit_card] or has_trump):
            return {"card": min_own_suit_card}
        else:
            return{"card":max_own_suit_card}

    # if we don't have cards that follow the suit
    # @example
    # the first player played "7H" (7 of hearts)
    #
    # we could either
    #
    # 1. throw any card
    # 2. reveal the trump

    # trump has not been revealed yet, and we don't know what the trump is
    # let's reveal the trump
    if (not trump_suit and not trump_revealed):
        return {"revealTrump": True}

    # we don't have any trump suit cards, throw random
    own_trump_suit_cards = get_suit_cards(own_cards, trump_suit)
    if (len(own_trump_suit_cards) == 0):
        for card in own_cards:
            if CARDS_DICT[card[0]]["points"] == 0:
                return {"card": card}
        return {"card": own_cards[-1]}

    did_reveal_the_trump_in_this_hand = trump_revealed and trump_revealed["playerId"] == own_id and trump_revealed["hand"] == (
        len(hand_history) + 1)

    # trump was revealed by me in this hand
    # or
    # I am going to reveal the trump, since I am the bidder

    if (is_bidder or did_reveal_the_trump_in_this_hand):
        response = {}
        if (is_bidder):
            response["revealTrump"] = True

        # if there are no trumps in the played
        if (len(get_suit_cards(played, trump_suit)) == 0):
            response["card"] = own_trump_suit_cards[-1]
            return response

        winning_trump_card_idx = pick_winning_card_idx(played, trump_suit)
        winning_card_player_idx = (first_turn + winning_trump_card_idx) % 4

        # if we revealed the trump in this round and the winning card is trump, there are two cases
        # 1. If the opponent is winning the hand, then you must throw the winning card of the trump suit against your opponent's card.
        # 2. If your partner is winning the hand, then you could throw any card of trump suit since your team is only winning the hand.
        if (winning_card_player_idx == my_partner_idx):
            response["card"] = own_trump_suit_cards[-1]
            return response

        winning_trump_card = played[winning_trump_card_idx]
        winning_card = find(own_trump_suit_cards, lambda card: is_high(
            card, winning_trump_card)) or own_trump_suit_cards[-1]

        # player who revealed the trump should throw the trump suit card
        return {"card": winning_card}

    return {"card": own_cards[-1]}
