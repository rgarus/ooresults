# Copyright (C) 2022 Rainer Garus
#
# This file is part of the ooresults Python package, a software to
# compute results of orienteering events.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from typing import Optional


handicap_male = {
    10: 0.7886,
    11: 0.8290,
    12: 0.8626,
    13: 0.8896,
    14: 0.9098,
    15: 0.9266,
    16: 0.9419,
    17: 0.9550,
    18: 0.9670,
    19: 0.9790,
    20: 0.9893,
    21: 0.9961,
    22: 0.9996,
    23: 1.0000,
    24: 1.0000,
    25: 1.0000,
    26: 1.0000,
    27: 1.0000,
    28: 0.9999,
    29: 0.9991,
    30: 0.9975,
    31: 0.9952,
    32: 0.9922,
    33: 0.9885,
    34: 0.9840,
    35: 0.9788,
    36: 0.9729,
    37: 0.9662,
    38: 0.9592,
    39: 0.9521,
    40: 0.9451,
    41: 0.9380,
    42: 0.9310,
    43: 0.9240,
    44: 0.9169,
    45: 0.9099,
    46: 0.9028,
    47: 0.8958,
    48: 0.8888,
    49: 0.8817,
    50: 0.8747,
    51: 0.8676,
    52: 0.8606,
    53: 0.8536,
    54: 0.8465,
    55: 0.8395,
    56: 0.8324,
    57: 0.8254,
    58: 0.8184,
    59: 0.8113,
    60: 0.8043,
    61: 0.7972,
    62: 0.7902,
    63: 0.7832,
    64: 0.7761,
    65: 0.7691,
    66: 0.7620,
    67: 0.7550,
    68: 0.7479,
    69: 0.7402,
    70: 0.7319,
    71: 0.7230,
    72: 0.7134,
    73: 0.7031,
    74: 0.6923,
    75: 0.6808,
    76: 0.6687,
    77: 0.6559,
    78: 0.6425,
    79: 0.6285,
    80: 0.6138,
    81: 0.5985,
    82: 0.5825,
    83: 0.5660,
    84: 0.5488,
    85: 0.5309,
    86: 0.5124,
    87: 0.4933,
    88: 0.4735,
    89: 0.4531,
    90: 0.4321,
}


handicap_female = {
    10: 0.7626,
    11: 0.7806,
    12: 0.7965,
    13: 0.8106,
    14: 0.8224,
    15: 0.8324,
    16: 0.8428,
    17: 0.8533,
    18: 0.8623,
    19: 0.8682,
    20: 0.8713,
    21: 0.8716,
    22: 0.8716,
    23: 0.8716,
    24: 0.8716,
    25: 0.8716,
    26: 0.8716,
    27: 0.8716,
    28: 0.8716,
    29: 0.8716,
    30: 0.8713,
    31: 0.8706,
    32: 0.8693,
    33: 0.8676,
    34: 0.8653,
    35: 0.8626,
    36: 0.8593,
    37: 0.8556,
    38: 0.8514,
    39: 0.8466,
    40: 0.8414,
    41: 0.8356,
    42: 0.8293,
    43: 0.8226,
    44: 0.8154,
    45: 0.8076,
    46: 0.7993,
    47: 0.7906,
    48: 0.7814,
    49: 0.7719,
    50: 0.7624,
    51: 0.7529,
    52: 0.7434,
    53: 0.7339,
    54: 0.7244,
    55: 0.7149,
    56: 0.7054,
    57: 0.6959,
    58: 0.6864,
    59: 0.6769,
    60: 0.6674,
    61: 0.6579,
    62: 0.6484,
    63: 0.6389,
    64: 0.6294,
    65: 0.6199,
    66: 0.6104,
    67: 0.6009,
    68: 0.5914,
    69: 0.5819,
    70: 0.5724,
    71: 0.5629,
    72: 0.5534,
    73: 0.5439,
    74: 0.5344,
    75: 0.5249,
    76: 0.5154,
    77: 0.5059,
    78: 0.4964,
    79: 0.4869,
    80: 0.4769,
    81: 0.4658,
    82: 0.4537,
    83: 0.4405,
    84: 0.4263,
    85: 0.4110,
    86: 0.3947,
    87: 0.3774,
    88: 0.3590,
    89: 0.3396,
    90: 0.3191,
}


class Handicap:
    male_year_min = min(handicap_male.keys())
    male_year_max = max(handicap_male.keys())
    male_max = max(handicap_male.values())

    female_year_min = min(handicap_female.keys())
    female_year_max = max(handicap_female.keys())
    female_max = max(handicap_female.values())

    def factor(self, female: bool, year: Optional[int]) -> float:
        if year is None:
            if female:
                return self.female_max
            else:
                return self.male_max
        else:
            if female:
                if year < self.female_year_min:
                    year = self.female_year_min
                elif year > self.female_year_max:
                    year = self.female_year_max
                return handicap_female[year]
            else:
                if year < self.male_year_min:
                    year = self.male_year_min
                elif year > self.male_year_max:
                    year = self.male_year_max
                return handicap_male[year]
