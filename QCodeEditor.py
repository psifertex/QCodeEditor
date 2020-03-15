#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Licensed under the terms of the MIT License 
https://github.com/luchko/QCodeEditor
@author: Ivan Luchko (luchko.ivan@gmail.com)

This module contains the light QPlainTextEdit based QCodeEditor widget which 
provides the line numbers bar and the syntax and the current line highlighting.

	class PythonHighlighter(QSyntaxHighlighter):
	class QCodeEditor(QPlainTextEdit):
				
testing and examples:

	def run_test():

Module is compatible with both pyQt4 and pyQt5

'''
try:
	import PyQt4 as PyQt
	pyQtVersion = "PyQt4"

except ImportError:
	try:
		import PyQt5 as PyQt
		pyQtVersion = "PyQt5"
	except ImportError:
		raise ImportError("neither PyQt4 or PyQt5 is found")

# imports requied PyQt modules
if pyQtVersion == "PyQt4":
	from PyQt4.QtCore import Qt, QRect, QRegExp
	from PyQt4.QtGui import (QWidget, QTextEdit, QPlainTextEdit, QColor, 
							 QPainter, QFont, QSyntaxHighlighter,
							 QTextFormat, QTextCharFormat)
else:
	from PyQt5.QtCore import Qt, QRect, QRegExp
	from PyQt5.QtWidgets import QWidget, QTextEdit, QPlainTextEdit
	from PyQt5.QtGui import (QColor, QPainter, QFont, QSyntaxHighlighter,
							 QTextFormat, QTextCharFormat) 
# classes definition

class PythonHighlighter(QSyntaxHighlighter):
	'''
	Class for highlighting xml text inherited from QSyntaxHighlighter

	reference:
		http://www.yasinuludag.com/blog/?p=49    
	
	'''
	def __init__(self, parent=None):
		
		super(PythonHighlighter, self).__init__(parent)
		
		self.highlightingRules = []

		numbersFormat = QTextCharFormat()
		numbersFormat.setForeground(QColor("#000070")) #blue
		self.highlightingRules.append((QRegExp(r"\d"), numbersFormat))
 
		stringFormat = QTextCharFormat()
		# xmlAttributeFormat.setFontItalic(True)
		stringFormat.setForeground(QColor("#177317")) #green
		self.highlightingRules.append((QRegExp("'(.*)'"), stringFormat))
		self.highlightingRules.append((QRegExp('"(.*)"'), stringFormat))
		# self.highlightingRules.append((QRegExp("="), xmlAttributeFormat))
	
		decoratorFormat = QTextCharFormat()
		decoratorFormat.setForeground(QColor("#e35e00")) #orange 
		self.highlightingRules.append((QRegExp("@.*"), decoratorFormat))

		operatorsFormat = QTextCharFormat()
		operatorsFormat.setForeground(QColor('#700000')) # red
		self.highlightingRules += [(QRegExp(exp), operatorsFormat) for exp in ("==", "!=", ">", "<", "(", ")", "/", "*", "-", "+")]
 
		singleLineCommentFormat = QTextCharFormat()
		singleLineCommentFormat.setForeground(QColor("#a0a0a4")) #grey
		self.highlightingRules.append((QRegExp("#(.*)"), singleLineCommentFormat))
		
		keywordFormat = QTextCharFormat()
		keywordFormat.setForeground(QColor("#000070")) #blue
		keywordFormat.setFontWeight(QFont.Bold) 
		keywordPatterns = ["print", "while", "for", "def", "class", "in", "is", "from", "import", "input", "if", "else"] 
		self.highlightingRules += [(QRegExp(pattern), keywordFormat)
				for pattern in keywordPatterns]
				
	#VIRTUAL FUNCTION WE OVERRIDE THAT DOES ALL THE COLLORING
	def highlightBlock(self, text):
		#for every pattern
		for expression, format in self.highlightingRules: 
			#Check what index that expression occurs at with the ENTIRE text
			index = expression.indexIn(text) 
			#While the index is greater than 0
			while index >= 0: 
				#Get the length of how long the expression is true, set the format from the start to the length with the text format
				length = expression.matchedLength()
				self.setFormat(index, length, format) 
				#Set index to where the expression ends in the text
				index = expression.indexIn(text, index + length) 
 
class QCodeEditor(QPlainTextEdit):
	'''
	QCodeEditor inherited from QPlainTextEdit providing:
		
		numberBar - set by DISPLAY_LINE_NUMBERS flag equals True
		curent line highligthing - set by HIGHLIGHT_CURRENT_LINE flag equals True
		setting up QSyntaxHighlighter

	references:
		https://john.nachtimwald.com/2009/08/19/better-qplaintextedit-with-line-numbers/    
		http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
	
	'''
	class NumberBar(QWidget):
		'''class that deifnes textEditor numberBar'''

		def __init__(self, editor):
			QWidget.__init__(self, editor)
			
			self.editor = editor
			self.editor.blockCountChanged.connect(self.updateWidth)
			self.editor.updateRequest.connect(self.updateContents)
			self.font = QFont()
			self.numberBarColor = QColor("#e8e8e8")
					 
		def paintEvent(self, event):
			
			painter = QPainter(self)
			painter.fillRect(event.rect(), self.numberBarColor)
			 
			block = self.editor.firstVisibleBlock()
 
			# Iterate over all visible text blocks in the document.
			while block.isValid():
				blockNumber = block.blockNumber()
				block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
 
				# Check if the position of the block is out side of the visible area.
				if not block.isVisible() or block_top >= event.rect().bottom():
					break
 
				# We want the line number for the selected line to be bold.
				if blockNumber == self.editor.textCursor().blockNumber():
					self.font.setBold(True)
					painter.setPen(QColor("#000000"))
				else:
					self.font.setBold(False)
					painter.setPen(QColor("#717171"))
				painter.setFont(self.font)
				
				# Draw the line number right justified at the position of the line.
				paint_rect = QRect(0, block_top, self.width(), self.editor.fontMetrics().height())
				painter.drawText(paint_rect, Qt.AlignRight, str(blockNumber+1))
 
				block = block.next()
 
			painter.end()
			
			QWidget.paintEvent(self, event)
 
		def getWidth(self):
			count = self.editor.blockCount()
			width = self.fontMetrics().width(str(count)) + 10
			return width      
		
		def updateWidth(self):
			width = self.getWidth()
			if self.width() != width:
				self.setFixedWidth(width)
				self.editor.setViewportMargins(width, 0, 0, 0);
 
		def updateContents(self, rect, scroll):
			if scroll:
				self.scroll(0, scroll)
			else:
				self.update(0, rect.y(), self.width(), rect.height())
			
			if rect.contains(self.editor.viewport().rect()):   
				fontSize = self.editor.currentCharFormat().font().pointSize()
				self.font.setPointSize(fontSize)
				self.font.setStyle(QFont.StyleNormal)
				self.updateWidth()
				
		
	def __init__(self, DISPLAY_LINE_NUMBERS=True, HIGHLIGHT_CURRENT_LINE=True,
				 SyntaxHighlighter=None, *args):        
		'''
		Parameters
		----------
		DISPLAY_LINE_NUMBERS : bool 
			switch on/off the presence of the lines number bar
		HIGHLIGHT_CURRENT_LINE : bool
			switch on/off the current line highliting
		SyntaxHighlighter : QSyntaxHighlighter
			should be inherited from QSyntaxHighlighter
		
		'''                  
		super(QCodeEditor, self).__init__()
		
		self.setFont(QFont("Ubuntu Mono", 11))
		self.setLineWrapMode(QPlainTextEdit.NoWrap)
							   
		self.DISPLAY_LINE_NUMBERS = DISPLAY_LINE_NUMBERS

		if DISPLAY_LINE_NUMBERS:
			self.number_bar = self.NumberBar(self)
			
		if HIGHLIGHT_CURRENT_LINE:
			self.currentLineNumber = None
			self.currentLineColor = self.palette().alternateBase()
			# self.currentLineColor = QColor("#e8e8e8")
			self.cursorPositionChanged.connect(self.highligtCurrentLine)
		
		if SyntaxHighlighter is not None: # add highlighter to textdocument
		   self.highlighter = SyntaxHighlighter(self.document())         
				 
	def resizeEvent(self, *e):
		'''overload resizeEvent handler'''
				
		if self.DISPLAY_LINE_NUMBERS:   # resize number_bar widget
			cr = self.contentsRect()
			rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
			self.number_bar.setGeometry(rec)
		
		QPlainTextEdit.resizeEvent(self, *e)

	def highligtCurrentLine(self):
		newCurrentLineNumber = self.textCursor().blockNumber()
		if newCurrentLineNumber != self.currentLineNumber:                
			self.currentLineNumber = newCurrentLineNumber
			hi_selection = QTextEdit.ExtraSelection() 
			hi_selection.format.setBackground(self.currentLineColor)
			hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
			hi_selection.cursor = self.textCursor()
			hi_selection.cursor.clearSelection() 
			self.setExtraSelections([hi_selection])           

##############################################################################
		 
if __name__ == '__main__':

	# TESTING        
	
	def run_test():
	
		print("\n {} is imported".format(pyQtVersion))
		# imports requied PyQt modules
		if pyQtVersion == "PyQt4":
			from PyQt4.QtGui import QApplication
		else:
			from PyQt5.QtWidgets import QApplication
		
		import sys
	   
		app = QApplication([])
		
		editor = QCodeEditor(DISPLAY_LINE_NUMBERS=True, 
							 HIGHLIGHT_CURRENT_LINE=True,
							 SyntaxHighlighter=PythonHighlighter)
		
# 		text = '''<FINITELATTICE>
#   <LATTICE name="myLattice">
# 	<BASIS>
# 	  <VECTOR>1.0 0.0 0.0</VECTOR>
# 	  <VECTOR>0.0 1.0 0.0</VECTOR>
# 	</BASIS>
#   </LATTICE>
#   <PARAMETER name="L" />
#   <PARAMETER default="L" name="W" />
#   <EXTENT dimension="1" size="L" />
#   <EXTENT dimension="2" size="W" />
#   <BOUNDARY type="periodic" />
# </FINITELATTICE>
# '''
		text = """\
def hello(text):
	print(text)

hello('Hello World')

# Comment"""
		editor.setPlainText(text)
		editor.resize(400,250)
		editor.show()
	
		sys.exit(app.exec_())

	
	run_test()
