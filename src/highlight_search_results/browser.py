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

from typing import Optional
import unicodedata

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMenu, QShortcut

from anki.find import Finder
from anki.hooks import addHook, wrap
from anki.lang import _
from aqt.browser import Browser

from .config import config

# ignore search token specifiers, search operators, and wildcard characters
excluded_tags = (
    "deck:",
    "tag:",
    "card:",
    "note:",
    "is:",
    "prop:",
    "added:",
    "rated:",
    "nid:",
    "cid:",
    "mid:",
    "seen:",
)
excluded_vals = ("*", "_", "_*")
operators = ("or", "and", "+")


def on_browser_did_change_row(
    browser: Browser, current: Optional[int] = None, previous: Optional[int] = None
):
    """
    Highlight search results in Editor pane on searching
    """
    if not browser._highlight_results:
        return

    txt = browser.form.searchEdit.lineEdit().text()

    txt = unicodedata.normalize("NFC", txt)

    if not txt or txt == _("<type here to search; hit enter to show =None deck>"):
        return

    tokens = Finder(browser.col)._tokenize(txt)

    vals = []

    for token in tokens:
        if (
            token in operators
            or token.startswith("-")
            or token.startswith(excluded_tags)
        ):
            continue
        if ":" in token:
            val = "".join(token.split(":")[1:])
            if not val or val in excluded_vals:
                continue
        else:
            val = token
        val = val.strip("""",*;""")
        vals.append(val)

    if not vals:
        return

    for val in vals:
        # FIXME: anki21 does not seem to support highlighting more than one
        # term at once. Likely a Qt bug / regression.
        # TODO: Perhaps choose to highlight the longest term on anki21.
        # TODO: Find a way to exclude UI text in editor pane from highlighting
        browser.editor.web.findText(val)


def on_custom_search(browser: Browser, onecard: Optional[bool] = False):
    """Extended search functions"""
    txt = browser.form.searchEdit.lineEdit().text().strip()
    cids = browser.col.findCards(txt, order=True)

    if onecard:
        # jump to next card, while wrapping around at the end
        if browser.card:
            cur = browser.card.id
        else:
            cur = None

        if cur and cur in cids:
            idx = cids.index(cur) + 1
        else:
            idx = None

        if not idx or idx >= len(cids):
            idx = 0
        cids = cids[idx : idx + 1]

    browser.form.tableView.selectionModel().clear()
    browser.model.selectedCards = {cid: True for cid in cids}
    browser.model.restoreSelection()


def toggle_search_highlights(browser: Browser, checked: bool):
    """Toggle search highlights on or off"""
    browser._highlight_results = checked
    if not checked:
        # clear highlights
        browser.editor.web.findText("")
    else:
        on_browser_did_change_row(browser, None, None)


def on_setup_search(browser: Browser):
    """Add extended search hotkeys"""
    shortcut = QShortcut(
        QKeySequence(config["local"]["hotkey_select_next_matching_card"]),
        browser.form.searchEdit,
    )
    shortcut.activated.connect(lambda: on_custom_search(browser, True))  # type: ignore
    shortcut = QShortcut(
        QKeySequence(config["local"]["hotkey_select_all_matching_cards"]),
        browser.form.searchEdit,
    )
    shortcut.activated.connect(lambda: on_custom_search(browser))  # type: ignore


def on_browser_menus_did_init(browser: Browser):
    """Setup menu entries and hotkeys"""
    browser._highlight_results = config["local"]["highlight_by_default"]
    try:
        # used by multiple add-ons, so we check for its existence first
        menu = browser.menuView
    except AttributeError:
        browser.menuView = QMenu(_("&View"))
        browser.menuBar().insertMenu(
            browser.mw.form.menuTools.menuAction(), browser.menuView
        )
        menu = browser.menuView
    menu.addSeparator()
    a = menu.addAction("Highlight Search Results")
    a.setCheckable(True)
    a.setChecked(browser._highlight_results)
    a.setShortcut(QKeySequence(config["local"]["hotkey_toggle_highlights"]))
    a.toggled.connect(lambda toggled: toggle_search_highlights(toggled, browser))


def initialize_browser():
    try:
        from aqt.gui_hooks import browser_menus_did_init

        browser_menus_did_init.append(on_browser_menus_did_init)
    except (ImportError, ModuleNotFoundError):
        addHook("browser.setupMenus", on_browser_menus_did_init)

    try:
        from aqt.gui_hooks import browser_did_change_row

        browser_did_change_row.append(on_browser_did_change_row)
    except (ImportError, ModuleNotFoundError):
        Browser._onRowChanged = wrap(
            Browser._onRowChanged, on_browser_did_change_row, "after"
        )

    # TODO: submit hook as PR
    Browser.setupSearch = wrap(Browser.setupSearch, on_setup_search, "after")
