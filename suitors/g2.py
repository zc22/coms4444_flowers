from typing import Dict

from flowers import Bouquet, Flower, FlowerSizes, FlowerColors, FlowerTypes
from suitors.base import BaseSuitor

import numpy as np
from copy import deepcopy
import random
from collections import defaultdict

"""
class FlowerSizes(Enum):
    Small = 0
    Medium = 1
    Large = 2
class FlowerColors(Enum):
    White = 0
    Yellow = 1
    Red = 2
    Purple = 3
    Orange = 4
    Blue = 5
class FlowerTypes(Enum):
    Rose = 0
    Chrysanthemum = 1
    Tulip = 2
    Begonia = 3
"""


class Suitor(BaseSuitor):
    def __init__(self, days: int, num_suitors: int, suitor_id: int):
        """
        :param days: number of days of courtship
        :param num_suitors: number of suitors, including yourself
        :param suitor_id: unique id of your suitor in range(num_suitors)
        """
        self.suitor_id = suitor_id
        self.scoring_parameters = {}
        self.other_suitors = []
        self.bouquets_given = defaultdict(list)
        self.turn = 1
        self.learning_rate = 10
        self.exploration_alpha = 0.3
        self.exploration_alpha_decay = self.exploration_alpha / days
        random_low = -1.0
        random_high = 1.0
        for i in range(num_suitors):
            if i != suitor_id:
                self.other_suitors.append(i)
                self.scoring_parameters[i] = {
                    FlowerSizes.Small: round(random.uniform(random_low,random_high), 2),
                    FlowerSizes.Medium: round(random.uniform(random_low,random_high), 2),
                    FlowerSizes.Large: round(random.uniform(random_low,random_high), 2),
                    FlowerColors.White: round(random.uniform(random_low,random_high), 2),
                    FlowerColors.Yellow: round(random.uniform(random_low,random_high), 2),
                    FlowerColors.Red: round(random.uniform(random_low,random_high), 2),
                    FlowerColors.Purple: round(random.uniform(random_low,random_high), 2),
                    FlowerColors.Orange: round(random.uniform(random_low,random_high), 2),
                    FlowerColors.Blue: round(random.uniform(random_low,random_high), 2),
                    FlowerTypes.Rose: round(random.uniform(random_low,random_high), 2),
                    FlowerTypes.Chrysanthemum: round(random.uniform(random_low,random_high), 2),
                    FlowerTypes.Tulip: round(random.uniform(random_low,random_high), 2),
                    FlowerTypes.Begonia: round(random.uniform(random_low,random_high), 2),
                }

        super().__init__(days, num_suitors, suitor_id, name='g2')

    def prepare_bouquet_for_group(self, group_id, flowers, copy_flower_counts, count = 4, rand=False, last=False):
        bouquet = defaultdict(int)
        bouquet_info = defaultdict(int)
        scoring_function = self.scoring_parameters[group_id]
        prev_bouquets = self.bouquets_given[group_id]
        if rand:
            random.shuffle(flowers)
            for _ in range(count):
                for item in flowers:
                    key,value = item
                    if copy_flower_counts[str(key)] <= 0:
                        continue
                    bouquet[key] += 1
                    copy_flower_counts[str(key)] -= 1
                    break
        elif last:
            can_best = True
            best_score = float('-inf')
            best_bouquet = None
            flower_counts = {}
            for p in prev_bouquets:
                score = p[1]
                b = p[0]
                if score > best_score:
                    best_score = score
                    best_bouquet = b
            if best_bouquet != None:
                for flower in best_bouquet.flowers():
                    if str(flower) in copy_flower_counts:
                        if copy_flower_counts[str(flower)] <= 0:
                            can_best = False
                            break
                        bouquet[flower] += 1
                        copy_flower_counts[str(flower)] -= 1
                        if str(flower) in flower_counts:
                            flower_counts[str(flower)] += 1
                        else:
                            flower_counts[str(flower)] = 1
                    else:
                        can_best = False
                        break
            else:
                can_best = False
            if not can_best:
                bouquet = defaultdict(int)
                for flower in flower_counts:
                    copy_flower_counts[flower] += flower_counts[flower]
                for _ in range(count):
                    best_flower = None
                    best_score = -10000
                    for item in flowers:
                        key,value = item
                        score = 0
                        if copy_flower_counts[str(key)] <= 0:
                            continue
                        
                        score += scoring_function[key.type] - bouquet_info[key.type]
                        score += scoring_function[key.color] - bouquet_info[key.color]
                        score += scoring_function[key.size] - bouquet_info[key.size]

                        if score > best_score:
                            best_score = score
                            best_flower = key
                    
                    if best_flower == None:
                        break
                    else:
                        bouquet[best_flower] += 1
                        copy_flower_counts[str(best_flower)] -= 1
        else:
            for _ in range(count):
                best_flower = None
                best_score = -10000
                for item in flowers:
                    key,value = item
                    score = 0
                    if copy_flower_counts[str(key)] <= 0:
                        continue
                    
                    score += scoring_function[key.type] - bouquet_info[key.type]
                    score += scoring_function[key.color] - bouquet_info[key.color]
                    score += scoring_function[key.size] - bouquet_info[key.size]

                    if score > best_score:
                        best_score = score
                        best_flower = key
                
                if best_flower == None:
                    break
                else:
                    bouquet[best_flower] += 1
                    copy_flower_counts[str(best_flower)] -= 1

        return (self.suitor_id, group_id, Bouquet(bouquet)), copy_flower_counts

    
    def prepare_bouquets(self, flower_counts: Dict[Flower, int]):
        """
        :param flower_counts: flowers and associated counts for for available flowers
        :return: list of tuples of (self.suitor_id, recipient_id, chosen_bouquet)
        the list should be of length len(self.num_suitors) - 1 because you should give a bouquet to everyone
            but yourself
        To get the list of suitor ids not including yourself, use the following snippet:
        all_ids = np.arange(self.num_suitors)
        recipient_ids = all_ids[all_ids != self.suitor_id]
        """
        bouquets = []

        copy_flower_counts = {}
        for key,value in flower_counts.items():
            copy_flower_counts[str(key)] = value 
        
        flowers = [(key,value) for key,value in flower_counts.items()]

        for o_id in self.other_suitors:
            r = random.uniform(0,1)
            if r < self.exploration_alpha or self.turn == 1:
                b, copy_flower_counts = self.prepare_bouquet_for_group(o_id, flowers, copy_flower_counts, rand=True)
            elif self.turn >= self.days:
                b, copy_flower_counts = self.prepare_bouquet_for_group(o_id, flowers, copy_flower_counts, rand=False, last=True)
            else: 
                b, copy_flower_counts = self.prepare_bouquet_for_group(o_id, flowers, copy_flower_counts) 
            self.bouquets_given[o_id].append([b[2]])
            bouquets.append(b)

        self.turn += 1
        self.exploration_alpha -= self.exploration_alpha_decay
        return bouquets

    def zero_score_bouquet(self):
        """
        :return: a Bouquet for which your scoring function will return 0
        """
        return Bouquet({})

    def one_score_bouquet(self):
        """
        :return: a Bouquet for which your scoring function will return 1
        """

        flower_1 = Flower(
            size=FlowerSizes.Small,
            color=FlowerColors.White,
            type=FlowerTypes.Rose
        )
        flower_2 = Flower(
            size=FlowerSizes.Small,
            color=FlowerColors.Yellow,
            type=FlowerTypes.Rose
        )
        flower_3 = Flower(
            size=FlowerSizes.Medium,
            color=FlowerColors.Red,
            type=FlowerTypes.Chrysanthemum
        )
        flower_4 = Flower(
            size=FlowerSizes.Medium,
            color=FlowerColors.Purple,
            type=FlowerTypes.Tulip
        )
        flower_5 = Flower(
            size=FlowerSizes.Large,
            color=FlowerColors.Orange,
            type=FlowerTypes.Begonia
        )
        flower_6 = Flower(
            size=FlowerSizes.Large,
            color=FlowerColors.Blue,
            type=FlowerTypes.Begonia
        )

        return Bouquet({
            flower_1: 1, 
            flower_2: 1,
            flower_3: 1,
            flower_4: 1,
            flower_5: 1,
            flower_6: 1,
        })

    def score_types(self, types: Dict[FlowerTypes, int]):
        """
        :param types: dictionary of flower types and their associated counts in the bouquet
        :return: A score representing preference of the flower types in the bouquet
        """

        type_scores = {
            FlowerTypes.Rose: 1/(3*4),
            FlowerTypes.Chrysanthemum: 0.5/(3*4),
            FlowerTypes.Tulip: 1/(3*4),
            FlowerTypes.Begonia: 1.5/(3*4),
        }

        num_types = 0
        for key,value in types.items():
            if value > 0:
                num_types += type_scores[key]
        return num_types
        

    def score_colors(self, colors: Dict[FlowerColors, int]):
        """
        :param colors: dictionary of flower colors and their associated counts in the bouquet
        :return: A score representing preference of the flower colors in the bouquet
        """
        num_types = 0
        for _,value in colors.items():
            if value > 0:
                num_types += (1 / (3 * 6))
        return num_types

    def score_sizes(self, sizes: Dict[FlowerSizes, int]):
        """
        :param sizes: dictionary of flower sizes and their associated counts in the bouquet
        :return: A score representing preference of the flower sizes in the bouquet
        """
        num_types = 0
        for _,value in sizes.items():
            if value > 0:
                num_types += (1 / (3 * 3))
        return num_types

    def adjust_scoring_function(self, prev_s, curr_s, o_id, bouquet):
        how_much = (curr_s - prev_s) * self.learning_rate

        if how_much > 0:
            return

        for size, value in bouquet.sizes.items():
            self.scoring_parameters[o_id][size] += how_much * value

        for t, value in bouquet.types.items():
            self.scoring_parameters[o_id][t] += how_much * value

        for color, value in bouquet.colors.items():
            self.scoring_parameters[o_id][color] += how_much * value


    def receive_feedback(self, feedback):
        """
        :param feedback:
        :return: nothing
        """
        index = 0
        for f in feedback:
            if index == self.suitor_id:
                index += 1
                continue

            self.bouquets_given[index][-1] += [f[0],f[1]]

            if self.turn > 2:
                prev_score = self.bouquets_given[index][-2][2]
                curr_score = f[1]
                self.adjust_scoring_function(prev_score, curr_score, index, self.bouquets_given[index][-1][0])

            index += 1

        self.feedback.append(feedback)