def main():
    card_count = int(input())
    cards = list(map(lambda x: int(x), input().rstrip().split()))
    cards.sort()
    
    group_list = []
    for card, i in enumurate(cards):
        if card + 1 == cards[i + 1] 

if __name__ == '__main__':
    main()