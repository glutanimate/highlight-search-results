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

from typing import List

from aqt.webview import AnkiWebView

def highlight_terms(webview: AnkiWebView, terms: List[str]):
    # FIXME: anki21 does not seem to support highlighting more than one
    # term at once. Likely a Qt bug / regression.
    # TODO: Perhaps choose to highlight the longest term on anki21.
    # TODO: Find a way to exclude UI text in editor pane from highlighting
    for term in terms:
        webview.findText(term)

def clear_highlights(webview: AnkiWebView):
    webview.findText("")
