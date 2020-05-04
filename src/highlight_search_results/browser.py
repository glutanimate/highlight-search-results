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

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QMenu, QShortcut

from anki.find import Finder
from anki.hooks import addHook, wrap
from anki.lang import _
from aqt.browser import Browser

from .config import config

find_flags = QWebEnginePage.FindFlags(0)

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


def on_row_changed(self, current, previous):
    """
    Highlight search results in Editor pane on searching
    """
    if not self._highlightResults:
        return

    txt = self.form.searchEdit.lineEdit().text()

    txt = unicodedata.normalize("NFC", txt)

    if not txt or txt == _("<type here to search; hit enter to show current deck>"):
        return

    tokens = Finder(self.col)._tokenize(txt)

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
        self.editor.web.findText(val, find_flags)


def on_custom_search(self, onecard=False):
    """Extended search functions"""
    txt = self.form.searchEdit.lineEdit().text().strip()
    cids = self.col.findCards(txt, order=True)

    if onecard:
        # jump to next card, while wrapping around at the end
        if self.card:
            cur = self.card.id
        else:
            cur = None

        if cur and cur in cids:
            idx = cids.index(cur) + 1
        else:
            idx = None

        if not idx or idx >= len(cids):
            idx = 0
        cids = cids[idx : idx + 1]

    self.form.tableView.selectionModel().clear()
    self.model.selectedCards = {cid: True for cid in cids}
    self.model.restoreSelection()


def toggle_search_highlights(self, checked):
    """Toggle search highlights on or off"""
    self._highlightResults = checked
    if not checked:
        # clear highlights
        self.editor.web.findText("", find_flags)
    else:
        on_row_changed(self, None, None)


def on_setup_search(self):
    """Add extended search hotkeys"""
    s = QShortcut(
        QKeySequence(config["local"]["hotkey_select_next_matching_card"]),
        self.form.searchEdit,
    )
    s.activated.connect(lambda: self.onCustomSearch(True))
    s = QShortcut(
        QKeySequence(config["local"]["hotkey_select_all_matching_cards"]),
        self.form.searchEdit,
    )
    s.activated.connect(self.onCustomSearch)


def on_setup_menus(self):
    """Setup menu entries and hotkeys"""
    self._highlightResults = config["local"]["highlight_by_default"]
    try:
        # used by multiple add-ons, so we check for its existence first
        menu = self.menuView
    except AttributeError:
        self.menuView = QMenu(_("&View"))
        self.menuBar().insertMenu(self.mw.form.menuTools.menuAction(), self.menuView)
        menu = self.menuView
    menu.addSeparator()
    a = menu.addAction("Highlight Search Results")
    a.setCheckable(True)
    a.setChecked(self._highlightResults)
    a.setShortcut(QKeySequence(config["local"]["hotkey_toggle_highlights"]))
    a.toggled.connect(self.toggleSearchHighlights)


def initialize_browser():
    addHook("browser.setupMenus", on_setup_menus)
    Browser._onRowChanged = wrap(Browser._onRowChanged, on_row_changed, "after")
    Browser.onCustomSearch = on_custom_search
    Browser.toggleSearchHighlights = toggle_search_highlights
    Browser.setupSearch = wrap(Browser.setupSearch, on_setup_search, "after")
