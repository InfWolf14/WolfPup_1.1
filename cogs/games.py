import asyncio
import json
from collections import Sequence

import discord
from discord.ext import commands
import random


class GamesCog(commands.Cog, name='games'):
    """Contains Games"""

    def __init__(self, bot):
        self.bot = bot
        self.cards = []
        self.card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        self.face_cards = ['King', 'Queen', 'Jack']
        self.suit_values = ['Spade', 'Heart', 'Club', 'Diamond']
        self.card_emojies = {'Spade': '\U00002660\U0000fe0f', 'Heart': '\U00002665\U0000fe0f',
                             'Club': '\U00002663\U0000fe0f', 'Diamond': '\U00002666\U0000fe0f'}

    def make_sequence(self, seq):
        if seq is None:
            return ()
        if isinstance(seq, Sequence) and not isinstance(seq, str):
            return seq
        else:
            return (seq,)

    def message_check(self, channel=None, author=None, content=None, ignore_bot=True, lower=True):
        channel = self.make_sequence(channel)
        author = self.make_sequence(author)
        content = self.make_sequence(content)
        if lower:
            content = tuple(c.lower() for c in content)

        def check(message):
            if ignore_bot and message.author.bot:
                return False
            if channel and message.channel not in channel:
                return False
            if author and message.author not in author:
                return False
            actual_content = message.content.lower() if lower else message.content
            if content and actual_content not in content:
                return False
            return True

        return check

    @commands.command(aliases=['bljk', 'black_jack'], name='blackjack')
    async def blackjack(self, ctx):
        """Generates a set of random numbers."""
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if str(ctx.channel.id) in config[str(ctx.guild.id)]['bot_channel'] or 'bot' in str(ctx.channel.name):

            if len(self.cards) > 45:
                self.cards = []
            game = True
            dealer = True
            dealer_cards = await self.deal()
            player_cards = await self.deal()
            dealer_total = 0
            player_total = 0
            dealer_card_string = ""
            player_card_string = ""
            hand1 = None
            hand2 = None
            dealer_dict = await self.hand_value(dealer_cards, self.bot.user, ctx.channel)
            dealer_total = dealer_dict['total']
            one_card_total = dealer_dict['dealer_total']
            dealer_card_string = dealer_dict['dealer']

            player_dict = await self.hand_value(player_cards, ctx.author, ctx.channel)
            player_total = player_dict['total']
            player_card_string = player_dict['card_string']

            dealer_message = await ctx.send(f'`Dealer Cards: {dealer_card_string}, score {one_card_total}`')
            player_message = await ctx.send(f'`Player Cards: {player_card_string}, score {player_total}`')

            dealer_message_id = dealer_message.id
            player_message_id = player_message.id


            player_bj_check = await self.blackjack_check(player_cards)
            dealer_bj_check = await self.blackjack_check(dealer_cards)

            if player_bj_check and player_total == 21 and not dealer_bj_check:
                await ctx.send('Blackjack!')
                return
            elif dealer_bj_check and player_bj_check:
                await ctx.send('Dealer pushes')
                return
            elif dealer_bj_check and not player_bj_check:
                await ctx.send('`You lose. Dealer Blackjack`')
                await dealer_message.edit(f'`Dealer Cards: {dealer_card_string}, score 21`')
                return

            i = 1
            hand = 1
            while game:
                try:
                    if "SPLIT" == player_cards[0][0]:
                        msg = f'Hand {hand}: Reply with Hit, Stand, or DoubleDown'
                    elif i == 1 and player_cards[0][0] == player_cards[1][0]:
                        msg = 'Reply with Hit, Stand, Split, or DoubleDown'
                    elif i == 1 and not player_cards[0][0] == player_cards[1][0]:
                        msg = 'Reply with Hit, Stand, or DoubleDown'
                    elif i > 1:
                        msg = 'Reply with Hit, or Stand'

                    play_message = await ctx.send(msg)

                    response = await self.bot.wait_for('message', timeout=20.0,
                                                       check=self.message_check(channel=ctx.message.channel))
                    await play_message.delete()
                    play_word = response.content
                    play_word = play_word.upper()
                    play_word = play_word.strip(" ")
                    await response.delete()

                except asyncio.TimeoutError:
                    await ctx.send('Timed out. Try again!')
                    return
                try:
                    if play_word == "SPLIT" and player_cards[0][0] == player_cards[1][0]:
                        hand1 = [player_cards[0]]
                        hand2 = [player_cards[1]]
                        player_cards = [["SPLIT", 0], [1, 1]]
                        card1 = await self.get_card()
                        card2 = await self.get_card()
                        hand1.append(list(card1))
                        hand2.append(list(card2))
                        await player_message.delete()
                        hand1_dict = await self.hand_value(hand1, ctx.author, ctx.channel)
                        hand1_string = hand1_dict['card_string']
                        hand1_total = hand1_dict['total']
                        hand2_dict = await self.hand_value(hand2, ctx.author, ctx.channel)
                        hand2_string = hand2_dict['card_string']
                        hand2_total = hand2_dict['total']
                        hand1_message = await ctx.send(f"`Hand 1 {hand1_string}. Score: {hand1_total}`")
                        hand2_message = await ctx.send(f'`Hand 2 {hand2_string}. Score: {hand2_total}`')
                except:
                    pass
                if play_word == "STAND" and hand == 1 and 'SPLIT' in player_cards:
                    hand = 2
                    continue
                if play_word == "HIT" or play_word == "DOUBLEDOWN":
                    if 'SPLIT' != player_cards[0][0]:
                        cards = await self.get_card()
                        player_cards.append(cards)
                        if play_word == "DOUBLEDOWN":
                            doubledown = True
                        else:
                            doubledown = False

                        player_dict = await self.hand_value(player_cards, ctx.author, ctx.channel)
                        player_total = player_dict['total']
                        player_card_string = player_dict['card_string']
                        await player_message.edit(content=f'`Player Cards: {player_card_string}, score {player_total}`')
                        if player_total > 21:
                            await ctx.send('You __**BUSTED**__')
                            return
                        elif doubledown:
                            break
                        elif player_total == 21:
                            break
                    elif "SPLIT" == player_cards[0][0]:
                        if hand == 1:
                            cards = await self.get_card()
                            hand1.append(cards)
                            if play_word == "DOUBLEDOWN":
                                doubledown = True
                            else:
                                doubledown = False
                            player_dict = await self.hand_value(hand1, ctx.author, ctx.channel)
                            hand1_total = player_dict['total']
                            hand1_string = player_dict['card_string']
                            await hand1_message.edit(content=f'`Hand 1 Player Cards: {hand1_string}, score {hand1_total}`')
                            if hand1_total > 21:
                                await ctx.send('You __**BUSTED**__')
                                hand = 2
                                continue
                            elif doubledown:
                                hand = 2
                                i += 1
                                continue
                            elif player_total == 21:
                                hand = 2
                                i += 1
                                continue
                            continue
                        if hand == 2:
                            cards = await self.get_card()
                            hand2.append(cards)
                            if play_word == "DOUBLEDOWN":
                                doubledown = True
                            else:
                                doubledown = False
                            player_dict = await self.hand_value(hand2, ctx.author, ctx.channel)
                            hand2_total = player_dict['total']
                            hand2_card_string = player_dict['card_string']
                            await hand2_message.edit(content=f'`**Hand 2** - Player Cards: {hand2_card_string}, score {hand2_total}`')
                            if player_total > 21:
                                await ctx.send('You __**BUSTED**__')
                                break
                            elif doubledown:
                                hand = 2
                                i += 1
                                break
                            elif player_total == 21:
                                hand = 2
                                i += 1
                                break
                            break

                    i += 1

                if play_word == "STAND" or (play_word == "DOUBLEDOWN" and i > 1):
                    break
            while dealer:
                if dealer_total >= 18:
                    break
                cards = await self.get_card()
                dealer_cards.append(cards)
                dealer_dict = await self.hand_value(dealer_cards, self.bot.user, ctx.channel)
                dealer_total = dealer_dict['total']
                dealer_card_string = dealer_dict['card_string']
                await dealer_message.edit(content=f'`Dealer Cards: {dealer_card_string}, score {dealer_total}`')
                if dealer_total > 21:
                    await ctx.send('Dealer __**BUSTED**__')
                    await player_message.clear_reactions()
                    return
                if dealer_total == 21:
                    dealer = False
                    break
                if dealer_total > 18:
                    dealer = False
                    break
            if player_cards[0][0] != 'SPLIT':
                if dealer_total == player_total:
                    await ctx.send("**Dealer pushes**")
                elif dealer_total > player_total:
                    await ctx.send("**Dealer** won")
                elif player_total > dealer_total:
                    await ctx.send("\U0001f387 **You won** \U0001f387")
            elif player_cards[0][0] == 'SPLIT':
                if hand1_total > dealer_total:
                    await ctx.send('**Won __Hand 1__**')
                elif hand1_total == dealer_total:
                    await ctx.send('**Dealer pushes on __Hand 1__**')
                elif hand1_total < dealer_total:
                    await ctx.send('**Dealer wins on __Hand 1__**')
                if hand2_total > dealer_total:
                    await ctx.send('**Won __Hand 2__**')
                elif hand2_total == dealer_total:
                    await ctx.send('**Dealer pushes on __Hand 2__**')
                elif hand2_total < dealer_total:
                    await ctx.send('**Dealer wins on __Hand 2__**')

    async def deal(self):
        card_1 = await self.get_card()
        self.cards.append(card_1)
        card_2 = await self.get_card()
        self.cards.append(card_2)
        dealt = [card_1, card_2]
        return dealt

    async def get_card(self):
        card = [random.choice(self.card_values), random.choice(self.suit_values)]
        if self.cards:
            while card in self.cards:
                card = [random.choice(self.card_values), random.choice(self.suit_values)]
        return card

    async def hand_value(self, cards, player, channel):
        dict = {}
        hand_total = 0
        card_string = ""
        x = 1
        acenumber = sum(x.count("Ace") for x in cards)

        for list in cards:
            for element in list:
                if element in self.card_values:
                    if element in self.face_cards:
                        hand_total += 10
                    elif isinstance(element, int):
                        if element < 11:
                            hand_total += element
                    elif 'Ace' in cards and player.bot:
                        hand_total += 11
                if element in self.card_values:
                    card_string += str(element)
                if element in self.card_emojies.keys():
                    emoji = self.card_emojies[element]
                    card_string += emoji
                    card_string += " "
        if not player.bot:
            if 'Ace' in card_string:
                while x <= acenumber:
                    try:
                        acemessage = await channel.send(f'`Value for your ace? 1 or 11. Cards are {card_string}`')
                        response = await self.bot.wait_for('message', timeout=20.0,
                                                           check=self.message_check(channel=channel))
                        if "1" == response.content:
                            acevalue = 1
                            x += 1
                            await acemessage.delete()
                            await response.delete()
                            hand_total += acevalue

                        elif "11" == response.content:
                            x += 1
                            acevalue = 11
                            await acemessage.delete()
                            await response.delete()
                            hand_total += acevalue

                        else:
                            await channel.send(f'Your response must be 1 or 11.', delete_after = 3)
                    except asyncio.TimeoutError:
                        await channel.send("Timeout. Try again.")
        if player.bot:
            dealer_total = cards[0][0]
            dealer_hand = str(cards[0][0]) + self.card_emojies[cards[0][1]]
            if 'Ace' in cards:
                dict['dealer_total'] = 11
            elif cards[0][0] in self.face_cards:
                dict['dealer_total'] = 10
            else:
                dict['dealer_total'] = dealer_total
            dict['dealer'] = dealer_hand

            if 'Ace' in cards:
                
                if len(cards) >= 3:
                    hand_total -= 10

        dict['total'] = hand_total
        dict['card_string'] = card_string
        return dict

    async def blackjack_check(self, cards):
        facecard = False
        ace = False
        for list in cards:
            for element in list:
                if element in self.face_cards:
                    facecard = True
            if 'Ace' in list:
                ace = True
        if facecard and ace:
            return True
        else:
            return False

    @commands.command(aliases = ['howtoblackjack','howto'])
    async def blackjackrules(self, ctx):
        embed = discord.Embed(title='How to play')
        embed.add_field(name= 'How to:', value='You will need to reply with the words in chat.')
        embed.add_field(name='What if I have an Ace?', value='You will need to say what you want your Ace to be '
                                                             'worth. You will need to reply with either a 1 or 11')
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(GamesCog(bot))
