# -*- coding: utf-8 -*-

# Highlight Search Results in the Browser Add-on for Anki
#
# Copyright (C) 2017-2020  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2006-2020 Ankitects Pty Ltd and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

from typing import Union, List, Tuple
from .libaddon.platform import checkAnkiVersion

# Query language properties

_ignored_tags: Tuple[str, ...] = (
    # default query language:
    "added:",
    "deck:",
    "note:",
    "tag:",
    "mid:",
    "nid:",
    "cid:",
    "card:",
    "is:",
    "flag:",
    "rated:",
    "dupe:",
    "prop:",
    # added by add-ons:
    "seen:",
    "rid:",
)

_ignored_values: Tuple[str, ...] = ("*", "_", "_*")
_operators: Tuple[str, ...] = ("or", "and", "+")
_stripped_chars: str = '",*;'

if checkAnkiVersion("2.1.24"):
    # 2.1.24+ only supports double-quotes
    _quotes: Tuple[str, ...] = ('"',)
    # TODO? don't drop nc
    _ignored_tags = _ignored_tags + ("re:", "nc:")
else:
    _quotes = ('"', "'")


# Utility functions

# TODO: check if this works for query language changes in 2.1.24+
# - support for escaped double-quotes (use "in_escape")
def tokenize_query(query: str) -> List[str]:
    """
    Tokenize search string
    
    Based on finder code in Anki versions 2.1.23 and lower
    (anki.find.Finder._tokenize)
    """

    in_quote: Union[bool, str] = False
    tokens: List[str] = []
    token: str = ""

    for c in query:
        # quoted text
        if c in _quotes:
            if in_quote:
                if c == in_quote:
                    in_quote = False
                else:
                    token += c
            elif token:
                # quotes are allowed to start directly after a :
                if token[-1] == ":":
                    in_quote = c
                else:
                    token += c
            else:
                in_quote = c
        # separator (space and ideographic space)
        elif c in (" ", "\u3000"):
            if in_quote:
                token += c
            elif token:
                # space marks token finished
                tokens.append(token)
                token = ""
        # nesting
        elif c in ("(", ")"):
            if in_quote:
                token += c
            else:
                if c == ")" and token:
                    tokens.append(token)
                    token = ""
                tokens.append(c)
        # negation
        elif c == "-":
            if token:
                token += c
            elif not tokens or tokens[-1] != "-":
                tokens.append("-")
        # normal character
        else:
            token += c
    # if we finished in a token, add it
    if token:
        tokens.append(token)

    return tokens


def get_searchable_tokens(tokens: List[str]) -> List[str]:
    searchable_tokens: List[str] = []

    for token in tokens:
        if (
            token in _operators
            or token.startswith("-")
            or token.startswith(_ignored_tags)
        ):
            continue
        
        if ":" in token:
            value = token.split(":", 1)[1]
            if not value or value in _ignored_values:
                continue
        else:
            value = token
        
        value = value.strip(_stripped_chars)
        
        searchable_tokens.append(value)

    return searchable_tokens
