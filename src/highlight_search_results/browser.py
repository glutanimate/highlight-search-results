# -*- coding: utf-8 -*-

# Highlight Search Results in the Browser Add-on for Anki
#
# Copyright (C) 2017-2020  Aristotelis P. <https://glutanimate.com/>
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

import unicodedata
from typing import List, Optional

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMenu, QShortcut

from aqt.browser import Browser

from .libaddon.platform import checkAnkiVersion

from .config import config
from .search import SearchTokenizer, QueryLanguageVersion
from .webview import clear_highlights, highlight_terms

_SEARCH_PLACEHOLDER: Optional[str]

if checkAnkiVersion("2.1.41"):
    # 2.1.41+ has no hard-coded place-holder text
    _SEARCH_PLACEHOLDER = None
else:
    try:
        from aqt.utils import tr, TR

        _SEARCH_PLACEHOLDER = tr(TR.BROWSING_TYPE_HERE_TO_SEARCH)  # type: ignore
    except Exception:
        from anki.lang import _

        _SEARCH_PLACEHOLDER = _("<type here to search; hit enter to show current deck>")

if checkAnkiVersion("2.1.24"):
    _query_language_version = QueryLanguageVersion.ANKI2124
else:
    _query_language_version = QueryLanguageVersion.ANKI2100

_search_tokenizer = SearchTokenizer(_query_language_version)


def on_browser_did_change_row(
    browser: Browser, current: Optional[int] = None, previous: Optional[int] = None
):
    """
    Highlight search results in Editor pane on searching
    """
    if not hasattr(browser, "_highlight_results") or not browser._highlight_results:
        return

    search_text = browser.form.searchEdit.lineEdit().text()

    search_text = unicodedata.normalize("NFC", search_text)

    if not search_text or search_text == _SEARCH_PLACEHOLDER:
        return

    tokens = _search_tokenizer.tokenize(search_text)
    searchable_tokens = _search_tokenizer.get_searchable_tokens(tokens)

    if not searchable_tokens:
        return

    highlight_terms(browser.editor.web, searchable_tokens)


def select_all_matching_cards(browser: Browser):
    matching_cids = _find_from_search_entry(browser)
    _set_card_selection(browser, matching_cids)


def select_next_matching_card(browser: Browser):
    matching_cids = _find_from_search_entry(browser)

    current_cid: Optional[int] = None if not browser.card else browser.card.id

    # jump to next card, while wrapping around at the end

    if current_cid and current_cid in matching_cids:
        next_index = matching_cids.index(current_cid) + 1
    else:
        next_index = None

    if next_index is None or next_index >= len(matching_cids):
        next_index = 0

    next_cid = matching_cids[next_index]

    _set_card_selection(browser, [next_cid])


def _find_from_search_entry(browser: Browser):
    search_text = browser.form.searchEdit.lineEdit().text().strip()
    return list(browser.col.findCards(search_text, order=True))


def _set_card_selection(browser: Browser, cids: List[int]):
    browser.form.tableView.selectionModel().clear()
    browser.model.selectedCards = {cid: True for cid in cids}
    browser.model.restoreSelection()


def toggle_search_highlights(browser: Browser, checked: bool):
    """Toggle search highlights on or off"""
    browser._highlight_results = checked
    if not checked:
        clear_highlights(browser.editor.web)
    else:
        on_browser_did_change_row(browser)


def on_browser_will_show(browser: Browser):
    """Add extended search hotkeys"""
    shortcut = QShortcut(
        QKeySequence(config["local"]["hotkey_select_next_matching_card"]),
        browser.form.searchEdit,
    )
    shortcut.activated.connect(  # type: ignore
        lambda: select_next_matching_card(browser)
    )

    shortcut = QShortcut(
        QKeySequence(config["local"]["hotkey_select_all_matching_cards"]),
        browser.form.searchEdit,
    )
    shortcut.activated.connect(  # type: ignore
        lambda: select_all_matching_cards(browser)
    )


def on_browser_menus_did_init(browser: Browser):
    """Setup menu entries and hotkeys"""
    browser._highlight_results = config["local"]["highlight_by_default"]

    try:
        # used by multiple add-ons, so we check for its existence first
        menu = browser.menuView
    except AttributeError:
        browser.menuView = QMenu("&View")
        browser.menuBar().insertMenu(
            browser.mw.form.menuTools.menuAction(), browser.menuView
        )
        menu = browser.menuView

    menu.addSeparator()

    a = menu.addAction("Highlight Search Results")
    a.setCheckable(True)
    a.setChecked(browser._highlight_results)
    a.setShortcut(QKeySequence(config["local"]["hotkey_toggle_highlights"]))
    a.toggled.connect(lambda toggled: toggle_search_highlights(browser, toggled))


def initialize_browser():
    try:
        from aqt.gui_hooks import browser_menus_did_init

        browser_menus_did_init.append(on_browser_menus_did_init)
    except (ImportError, ModuleNotFoundError):
        from anki.hooks import addHook

        addHook("browser.setupMenus", on_browser_menus_did_init)

    try:
        from aqt.gui_hooks import browser_did_change_row

        browser_did_change_row.append(on_browser_did_change_row)
    except (ImportError, ModuleNotFoundError):
        from anki.hooks import wrap

        Browser._onRowChanged = wrap(
            Browser._onRowChanged, on_browser_did_change_row, "after"
        )

    try:
        from aqt.gui_hooks import browser_will_show

        browser_will_show.append(on_browser_will_show)
    except (ImportError, ModuleNotFoundError):
        from anki.hooks import wrap

        Browser.setupSearch = wrap(Browser.setupSearch, on_browser_will_show, "after")
