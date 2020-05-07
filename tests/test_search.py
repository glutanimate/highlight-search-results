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

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from highlight_search_results.search import SearchTokenizer


def _assert_common_tokenizations(tokenizer: "SearchTokenizer"):
    assert tokenizer.tokenize("hello world") == ["hello", "world"]
    assert tokenizer.tokenize("hello  world") == ["hello", "world"]
    assert tokenizer.tokenize("one -two") == ["one", "-", "two"]
    assert tokenizer.tokenize("one --two") == ["one", "-", "two"]
    assert tokenizer.tokenize("one - two") == ["one", "-", "two"]
    assert tokenizer.tokenize("one or -two") == ["one", "or", "-", "two"]
    assert tokenizer.tokenize('"hello world"') == ["hello world"]
    assert tokenizer.tokenize("one (two or ( three or four))") == [
        "one",
        "(",
        "two",
        "or",
        "(",
        "three",
        "or",
        "four",
        ")",
        ")",
    ]
    assert tokenizer.tokenize("embedded'string") == ["embedded'string"]


def test_tokenization_2120(mock_skip_addon_init):

    from highlight_search_results.search import SearchTokenizer, QueryLanguageVersion

    tokenizer = SearchTokenizer(QueryLanguageVersion.ANKI2100)

    _assert_common_tokenizations(tokenizer)
    # assert tokenizer.tokenize("'hello \"world\"'") == ['hello "world"']
    # assert tokenizer.tokenize("deck:'two words'") == ["deck:two words"]


def test_tokenization_2124(mock_skip_addon_init):

    from highlight_search_results.search import SearchTokenizer, QueryLanguageVersion

    tokenizer = SearchTokenizer(QueryLanguageVersion.ANKI2100)

    _assert_common_tokenizations(tokenizer)
    # assert tokenizer.tokenize("'hello \"world\"'") == ['hello "world"']
    # assert tokenizer.tokenize("deck:'two words'") == ["deck:two words"]
