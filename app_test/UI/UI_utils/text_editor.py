from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import QPlainTextEdit


class SyntaxHighlighter(QPlainTextEdit):
    def __init__(self, app, ui):
        super().__init__()
        self.highlight_rules = []
        self.setup_default_highlighting()
        self.highlight_text()

    def setup_default_highlighting(self):
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#AA0000"))  # Red color
        keywords = ["if", "else", "for", "while"]  # Example keywords
        for word in keywords:
            pattern = rf"\b{word}\b"
            rule = (pattern, keyword_format)
            self.highlight_rules.append(rule)

    def highlight_text(self):
        cursor = self.textCursor()
        text = self.toPlainText()

        for pattern, format in self.highlight_rules:
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, length)
                cursor.setCharFormat(format)

        self.setTextCursor(cursor)
