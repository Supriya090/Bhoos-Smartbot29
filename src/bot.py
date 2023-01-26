from utils import get_suit, get_player_bid, get_min_max_cards, get_suit_cards, get_partner_idx, pick_winning_card_idx, is_high, index, find, sort_dict


def get_bid(body):
    MIN_BID = 16
    PASS_BID = 0

    own_cards = body["cards"]

    # Considering J and 9 as strong cards
    strong_cards = {'J':0, '9':0, 'A':0, 'T':0}
    for idx in range(len(own_cards)):
        card = own_cards[idx][0]
        if card in strong_cards:
            if card == 'J':
                strong_cards[card] += 3
            elif card == '9':
                strong_cards[card] += 2
            else:
                strong_cards[card] += 1

    strong_cards_sum = sum(strong_cards.values())
    # print("\n\nStrong cards", strong_cards)

    bid_history = body["bidHistory"]
    # when you are the first player to bid, use the minimum bid
    if len(bid_history) == 0:
        return {"bid": MIN_BID}

    # Determining the last max bid
    bid_list = []
    for i in bid_history:
        bid_list.append(i[1])
    last_max_bid = max(bid_list)
    # print("\n\n Last Bid1", last_max_bid)

    # Determining the suits of your card
    initial_suit_list = []
    for card in own_cards:
        initial_suit_list.append(get_suit(card))
    
    isDefender = True if body["playerId"] == body["bidState"]["defenderId"] else False
    print("\n\n PlayerId", body["playerId"])
    print("\n\n DefenderId", body["bidState"]["defenderId"])

    # Avoid bidding when you have one card from each suit.
    if(len(set(initial_suit_list)) == 4 and strong_cards["J"]/3 <= 1):
        return {"bid": PASS_BID}    

    # If you have three or more cards of the same suit, bid up to 18
    # If you have four cards of the same suit, bid up to 20
    max_suit = max(set(initial_suit_list), key = initial_suit_list.count)

    max_suit_count = initial_suit_list.count(max_suit)
    _, max_own_card, _ = get_min_max_cards(own_cards)

    suitable_bid = get_player_bid(last_max_bid, isDefender)
    if(len(set(initial_suit_list)) == 1 and last_max_bid < 19 and last_max_bid != 0):
        return{"bid": suitable_bid}
    if(len(set(initial_suit_list)) <= 2):
        if(last_max_bid == 0):
            return {"bid": MIN_BID}
        if(strong_cards["J"]/3 <= 1 and last_max_bid < 17):
            return {"bid": suitable_bid}
        elif(max_own_card[0] == 'J' and get_suit(max_own_card) == max_suit and max_suit_count > 2 and last_max_bid < 18):
            return {"bid": suitable_bid}
        elif(strong_cards["J"]/3 > 1 and last_max_bid < 19):
            return {"bid": suitable_bid}
        else:
            return {"bid": PASS_BID}

    # when you have two or more J or 9, go to a higher bid
    # if the bid is already 18, pass
    if(strong_cards_sum >= 5 and last_max_bid != 0):
        if(strong_cards["J"]/3 <= 1 and last_max_bid < 17):
            return {"bid": suitable_bid}
        elif(strong_cards["J"]/3 > 1 and last_max_bid < 18):
            return {"bid": suitable_bid}
        elif(strong_cards["J"]/3 > 1 and len(set(initial_suit_list)) <= 2 and last_max_bid < 19):
            return {"bid": suitable_bid}
        else:
            return {"bid": PASS_BID}
    else:
        return {"bid": PASS_BID}
        

    # For choose_trump_suit testing purposes
    # if last_max_bid < 19:
    #     return{"bid": last_max_bid + 1}
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
    own_cards_dict, max_own_card, min_own_card = get_min_max_cards(own_cards)
    sorted_own_card_dict = sort_dict(own_cards_dict)
    # if we are the one to throw the first card in the hands, throw the highest card
    if (not first_card):
        if(((len(own_cards) == 8) or (len(own_cards) == 7) or (len(own_cards) == 6)) and max_own_card[0] != 'J'):
            if(get_suit(min_own_card) != trump_suit):
                return{"card": min_own_card}
            else:
                return{"card": list(sorted_own_card_dict)[1]}
        else:
            if(len(own_cards) > 1):
                if(get_suit(max_own_card) == trump_suit and list(sorted_own_card_dict)[-2][0] == max_own_card[0]):
                    return{"card": list(sorted_own_card_dict)[-2]}
                else:
                    return{"card": max_own_card}
            else:
                return{"card": max_own_card}
    
    first_card_suit = get_suit(first_card)
    own_suit_cards = get_suit_cards(own_cards, first_card_suit)

    # Getting played card info
    played_card_dict, max_played_card, _ = get_min_max_cards(played)
    sorted_played_card_dict = sort_dict(played_card_dict)
    played_suits = [get_suit(card) for card in played]
    has_trump = True if trump_suit in played_suits else False

    partner_card = list(played_card_dict.keys())[len(played) - 2]
    
    # if we have the suit with respect to the first card, we throw it
    if len(own_suit_cards) > 0:
        own_suit_card_dict, max_own_suit_card, min_own_suit_card = get_min_max_cards(own_suit_cards)
        sorted_own_suit_card_dict = sort_dict(own_suit_card_dict)
        print("\n\n", max_own_suit_card, max_played_card, min_own_suit_card)

        # If your partner has thrown the highest card, increase points by throwing your highest
        # If a trump is involved in the mix, and is not thrown by your partner, throw the lowest card
        if(len(played) > 1):
            print("\n\n Partner's card", partner_card)
            if(has_trump and trump_suit != first_card_suit):
                played_trump_suit_cards = get_suit_cards(played, trump_suit)
                played_trump_suit_cards_dict, max_played_trump_suit_card, _ = get_min_max_cards(played_trump_suit_cards)
                if(len(played_suits)>1):
                    if(trump_suit != partner_card[1] or max_played_trump_suit_card != partner_card):
                        return{"card":min_own_suit_card}
                    else:
                        return{"card":max_own_suit_card}
            else:
                if (played_card_dict[max_played_card] < own_suit_card_dict[max_own_suit_card]):
                    min_winning_card = max_own_suit_card
                    for own_suit_card in sorted_own_suit_card_dict:
                        if(played_card_dict[max_played_card] < own_suit_card_dict[own_suit_card]):
                            print("\n\n Partner's card", own_suit_card)
                            min_winning_card = own_suit_card
                            break
                    return{"card":min_winning_card}
                if(max_played_card == partner_card):
                    return{"card":max_own_suit_card}
                else:
                    return{"card": min_own_suit_card}
                
        # We throw the highest one if we have one higher than highest played card
        # Else we throw the lowest card
        # print("\n\n", has_trump)
        if (played_card_dict[max_played_card] > own_suit_card_dict[max_own_suit_card] or has_trump):
            return {"card": min_own_suit_card}
        else:
            min_winning_card = max_own_suit_card
            for own_suit_card in sorted_own_suit_card_dict:
                if(played_card_dict[max_played_card] < sorted_own_suit_card_dict[own_suit_card]):
                    min_winning_card = own_suit_card
                    break
            return{"card":min_winning_card}

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
    if(len(played) > 1 and max_played_card == partner_card and played_card_dict[max_played_card] > 1 and not trump_revealed):
        max_non_trump_card = max_own_card
        desc_sorted_own_card_dict = sort_dict(own_cards_dict, True)
        if(is_bidder):
            for card in desc_sorted_own_card_dict:
                if get_suit(card) != trump_suit:
                    max_non_trump_card = card
                    break
        return {"card": max_non_trump_card}
    
    print("\n\n", not trump_revealed)
    if(played_card_dict[max_played_card] < 1 and not trump_revealed):
        min_non_trump_card = min_own_card
        if(is_bidder):
            for card in sorted_own_card_dict:
                if get_suit(card) != trump_suit:
                    min_non_trump_card = card
                    break
        return {"card": min_non_trump_card}

    if (not trump_suit and not trump_revealed):
        return {"revealTrump": True}

    # Get my min and max trump suit cards
    own_trump_suit_cards = get_suit_cards(own_cards, trump_suit)
    played_trump_suit_cards = get_suit_cards(played, trump_suit)
    # we don't have any trump suit cards, throw minimum
    # If partner has the highest throw maximum
    if (len(own_trump_suit_cards) == 0):
        if(len(played) > 1):
            print("\n\n Partner's card", partner_card)
            if(max_played_card == partner_card):
                # If among the multiple max cards played, one of them is trump and the trump is not partner's, return the min card
                if(has_trump and get_suit(partner_card) != trump_suit):
                    return{"card": min_own_card}
                # if(list(sorted_played_card_dict)[-1][0] == list(sorted_played_card_dict)[-2][0]):
                #     return{"card": min_own_card}
                return{"card":max_own_card}
            else:
                return {"card": min_own_card}
        return{"card": min_own_card}
    else:
        own_trump_suit_cards_dict, max_trump_suit_card ,min_trump_suit_card = get_min_max_cards(own_trump_suit_cards)
        response = {}
        if (not trump_revealed):
            response["revealTrump"]= True
        if(len(played_trump_suit_cards) == 0):
            if(len(played) > 1):
                if(max_played_card == partner_card):
                    if(max_trump_suit_card[0] == 'J' or max_trump_suit_card[0] == '9'):
                        response["card"] = min_trump_suit_card
                    else:
                        response["card"] = max_trump_suit_card
                else:
                    response["card"] = min_trump_suit_card
                return response   
            # If max played card has no points, do not waste your trump card, throw a random card 
            # if(played_card_dict[max_played_card] > 1):
            #     response["card"]= min_trump_suit_card
            # else:
            #     response["card"]= min_own_card
            # return response
            response["card"] = min_trump_suit_card
            return response
        else:
            sorted_own_trump_suit_cards = sort_dict(own_trump_suit_cards_dict)
            played_trump_suit_cards_dict, max_played_trump_suit_card, _ = get_min_max_cards(played_trump_suit_cards)
            if(played_trump_suit_cards_dict[max_played_trump_suit_card] < own_trump_suit_cards_dict[max_trump_suit_card]):
                min_winning_card = max_trump_suit_card
                for own_trump_suit_card in sorted_own_trump_suit_cards:
                    if(played_trump_suit_cards_dict[max_played_trump_suit_card] < sorted_own_trump_suit_cards[own_trump_suit_card]):
                        min_winning_card = own_trump_suit_card
                        break
                response["card"]=min_winning_card
                return response
            

    did_reveal_the_trump_in_this_hand = trump_revealed and trump_revealed["playerId"] == own_id and trump_revealed["hand"] == (
        len(hand_history) + 1)

    # trump was revealed by me in this hand
    # or
    # I am going to reveal the trump, since I am the bidder
    if (is_bidder or did_reveal_the_trump_in_this_hand):
        response = {}
        # If my partner is winning and I am the bidder, throw your highest card, doesn't have to be a trump
        if (is_bidder):
            if (not trump_revealed):
                response["revealTrump"] = True
            if(len(played) > 1):
                has_own_trump = True if trump_suit in own_cards else False
                if(max_played_card == partner_card and has_own_trump):
                    response["card"] = max_trump_suit_card
                return response

        _, max_trump_suit_card ,min_trump_suit_card = get_min_max_cards(own_trump_suit_cards)
        # if there are no trumps in the played, throw your minimum trump suit card
        if (len(played_trump_suit_cards) == 0):
            print("\n\n Goes here")
            # return{"revealTrump": True}
            if (not trump_revealed):
                response["revealTrump"] = True
            response["card"] = min_trump_suit_card
            return response

        winning_trump_card_idx = pick_winning_card_idx(played, trump_suit)
        winning_card_player_idx = (first_turn + winning_trump_card_idx) % 4

        # if we revealed the trump in this round and the winning card is trump, there are two cases
        # 1. If the opponent is winning the hand, then you must throw the winning card of the trump suit against your opponent's card.
        # 2. If your partner is winning the hand, then you could throw any card of trump suit since your team is only winning the hand.
        if (winning_card_player_idx == my_partner_idx):
            response["card"] = max_trump_suit_card
            return response

        winning_trump_card = played[winning_trump_card_idx]
        winning_card = find(own_trump_suit_cards, lambda card: is_high(
            card, winning_trump_card)) or own_trump_suit_cards[-1]

        # player who revealed the trump should throw the trump suit card
        return {"card": winning_card}

    return {"card": own_cards[-1]}