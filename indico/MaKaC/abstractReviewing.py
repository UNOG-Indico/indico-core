# -*- coding: utf-8 -*-
##
##
## This file is part of CDS Indico.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Indico; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from persistent import Persistent
from MaKaC.common.Counter import Counter
from MaKaC.reviewing import Question
from MaKaC.errors import MaKaCError


class ConferenceAbstractReview(Persistent):
    """
    This class manages the parameters of the abstract reviewing.
    """

    def __init__(self, conference):
        """
        conference must be a Conference object (not an id).
        """
        self._conference = conference
        self._reviewingQuestions = []

        # by default
        self._numberOfAnswers = 7
        self._scaleLower = 0
        self._scaleHigher = 10
        self._radioButtonsLabels = ["0", "", "", "5", "", "", "10"]
        self._radioButtonsTitles = ["0", "1.7", "3.3", "5", "6.7", "8.3", "10"]
        self._questionCounter = Counter(1)
        self._answerCounter = Counter(1)
        self.notifyModification()

    def getConference(self):
        """ Returns the parent conference of the ConferencePaperReview object
        """
        return self._conference

    def addReviewingQuestion(self, text):
        """ Adds this question at the end of the list of questions
        """
        newId = self._getNewQuestionId()
        question = Question(newId, text)
        self._reviewingQuestions.append(question)
        self.notifyModification()

    def getReviewingQuestions(self):
        """ Returns the list of questions
        """
        return self._reviewingQuestions

    def removeReviewingQuestion(self, questionId, keepJud):
        """ Removes a question from the list
        """
        question = self.getQuestionById(questionId)

        if question:
            self._reviewingQuestions.remove(question)
            self.notifyModification()
        else:
            raise MaKaCError("Cannot remove a question which doesn't exist")

    def editReviewingQuestion(self, questionId, text):
        """ Edit the text of a question """
        question = self.getQuestionById(questionId)

        if question:
            question.setText(text)
            self.notifyModification()
        else:
            raise MaKaCError("Cannot edit a question which doesn't exist")

    def getQuestionNames(self):
        """ Return the names of the questions which are shown in the webpage """
        names = []
        for question in self._reviewingQuestions:
            names.append(question.getName())
        return names

    def getQuestionById(self, questionId):
        """ Return the question with the especified id """
        for question in self._reviewingQuestions:
            if (questionId == question.getId()):
                return question

    def setNumberOfAnswers(self, num):
        """ Set the number of possible answers (radio buttons) """
        self._numberOfAnswers = num

    def getNumberOfAnswers(self):
        """ Returns the number of possible answers """
        return self._numberOfAnswers

    def setRadioButtonsLabels(self):
        """ Set the labels for the radio buttons """
        self._radioButtonsLabels = []
        i = 0
        while i < self.getNumberOfAnswers():
            # first label
            if i == 0:
                self._radioButtonsLabels.append(str(self.getScaleLower()))
            # last label
            elif i == self._numberOfAnswers - 1:
                self._radioButtonsLabels.append(str(self.getScaleHigher()))
            # if there is a middle value (odd number of values) and we are there
            elif (self.getNumberOfAnswers() % 2 == 1) and  (i ==  (self.getNumberOfAnswers() - 1) / 2):
                # check if we need float division
                if ((self.getScaleLower() + self.getScaleHigher()) % 2 == 0):
                    label = str((self.getScaleLower() + self.getScaleHigher()) / 2)
                    self._radioButtonsLabels.append(label)
                else:
                    label = str((self.getScaleLower() + self.getScaleHigher()) / float(2))
                    self._radioButtonsLabels.append(label)
            else:
                self._radioButtonsLabels.append("")
            i += 1
        self.notifyModification()

    def setRadioButtonsTitles(self):
        """ Set the titles for the radio buttons """
        self._radioButtonsTitles = []
        i = 0
        while i < self.getNumberOfAnswers():
            # check if we need float division
            if ((i * self.getScaleHigher()) % (self.getNumberOfAnswers() - 1) == 0):
                title = "%.0f" % (((self.getScaleHigher() - self.getScaleLower()) / float(self.getNumberOfAnswers()-1)) * i + self.getScaleLower())
                self._radioButtonsTitles.append(title)
            else:
                title = "%.1f" % (((self.getScaleHigher() - self.getScaleLower()) / float(self.getNumberOfAnswers()-1)) * i + self.getScaleLower())
                self._radioButtonsTitles.append(title)
            i += 1
        self.notifyModification()

    def getRadioButtonsTitles(self):
        """ Get the titles for the radio buttons """
        return self._radioButtonsTitles

    def getScaleLower(self):
        return self._scaleLower

    def getScaleHigher(self):
        return self._scaleHigher

    def getRadioButtonsLabels(self):
        """ Get the labels for the radio buttons """
        return self._radioButtonsLabels

    def setScale(self, min, max):
        """ Set the scale for the rating and labels """
        self._scaleLower = min
        self._scaleHigher = max

    def _getNewQuestionId(self):
        """ Returns a new an unused questionId
            Increments the questionId counter
        """
        return self._questionCounter.newCount()

    def getNewAnswerId(self):
        """ Returns a new an unused answerId
            Increments the answerId counter
        """
        return self._answerCounter.newCount()

    def notifyModification(self):
        """ Notifies the DB that a list or dictionary attribute of this object has changed
        """
        self._p_changed = 1
