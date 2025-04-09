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

import itertools


def highlight_terms(webview: AnkiWebView, terms: List[str], scroll_to_first: bool = True):
    # JavaScript to highlight terms using a transparent overlay
    script = """
			function removeHighlights() {
					var highlights = document.querySelectorAll('.highlight-overlay');
					highlights.forEach(function(highlight) {
							highlight.parentNode.removeChild(highlight);
					});
			}

			function highlightTerm(term, color, scrollToFirst) {
					var textNodes = [];
					var firstHighlight = null;
					function getTextNodes(node) {
							if (node.nodeType === Node.TEXT_NODE) {
									textNodes.push(node);
							} else {
									for (var i = 0; i < node.childNodes.length; i++) {
											getTextNodes(node.childNodes[i]);
									}
							}
					}
					getTextNodes(document.body);

					textNodes.forEach(function(node) {
							var startIndex = 0;
							var index;
							while ((index = node.nodeValue.toLowerCase().indexOf(term.toLowerCase(), startIndex)) > -1) {
									var range = document.createRange();
									range.setStart(node, index);
									range.setEnd(node, index + term.length);
									var rect = range.getBoundingClientRect();

									var highlight = document.createElement('div');
									highlight.className = 'highlight-overlay';
									highlight.style.position = 'absolute';
									highlight.style.left = rect.left + 'px';
									highlight.style.top = rect.top + window.scrollY + 'px';
									highlight.style.width = rect.width + 'px';
									highlight.style.height = rect.height + 'px';
									highlight.style.backgroundColor = color;
									highlight.style.pointerEvents = 'none';
									highlight.style.zIndex = '9999';
									document.body.appendChild(highlight);

									if (scrollToFirst && !firstHighlight) {
										firstHighlight = highlight;
									}

									startIndex = index + term.length;
							}
					});

					if (firstHighlight) {
						firstHighlight.scrollIntoView({behavior: 'smooth', block: 'center'});
					}
			}

			removeHighlights();
			%s
    """
    colors = ['rgba(255, 255, 0, 0.5)', "rgba(255, 0, 0, 0.5)", "rgba(0, 255, 0, 0.5)", "rgba(0, 0, 255, 0.5)", 'rgba(0, 255, 255, 0.5)', 'rgba(255, 0, 255, 0.5)']
    color_cycle = itertools.cycle(colors)
    
    terms_script = "\n".join([f"highlightTerm('{term}', '{next(color_cycle)}', {str(scroll_to_first).lower()});" for term in terms])
    webview.page().runJavaScript(script % terms_script)

def clear_highlights(webview: AnkiWebView):
    # webview.findText("good")
    # from aqt.qt import debug; debug()
    webview.page().runJavaScript("removeHighlights();")
