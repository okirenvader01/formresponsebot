class DistributionManager:
    """
    Stores and validates response distributions for form questions.
    """

    def __init__(self, questions):
        self.questions = questions
        self.distributions = {}

    def set_distribution(self, question_id, percentages):
        """
        Set the distribution for a question.

        For multiple-choice, linear-scale, and dropdown questions,
        percentages must total 100.

        For checkbox questions, percentages are independent and
        therefore do not need to total 100.

        Percentages are supplied as a list matching the question's
        option order. Internally they are stored as:
        
            {
                "Option A": 50,
                "Option B": 30,
                "Option C": 20
            }
        """

        question = self._find_question(question_id)

        if question is None:
            raise ValueError(
                f"Question ID {question_id} was not found."
            )

        question_type = question["type"]
        options = question.get("options", [])

        # --------------------------------------------------------------
        # MCQ / LINEAR SCALE / DROPDOWN
        # --------------------------------------------------------------

        if question_type in {
            "multiple_choice",
            "linear_scale",
            "dropdown"
        }:

            if len(percentages) != len(options):
                raise ValueError(
                    f"Question {question_id} has "
                    f"{len(options)} options, but "
                    f"{len(percentages)} percentages were supplied."
                )

            total = sum(percentages)

            if abs(total - 100) > 0.001:
                raise ValueError(
                    f"Percentages for question {question_id} "
                    f"must total 100. Current total: {total}"
                )

        # --------------------------------------------------------------
        # CHECKBOX
        # --------------------------------------------------------------

        elif question_type == "checkbox":

            if len(percentages) != len(options):
                raise ValueError(
                    f"Question {question_id} has "
                    f"{len(options)} options, but "
                    f"{len(percentages)} percentages were supplied."
                )

        # --------------------------------------------------------------
        # UNSUPPORTED QUESTION TYPE
        # --------------------------------------------------------------

        else:

            raise ValueError(
                f"Question type '{question_type}' "
                f"does not use distributions."
            )

        # --------------------------------------------------------------
        # CONVERT LIST TO OPTION -> PERCENTAGE DICTIONARY
        # --------------------------------------------------------------

        self.distributions[question_id] = {
            option: percentage
            for option, percentage in zip(
                options,
                percentages
            )
        }

    def _find_question(self, question_id):
        """Find a question by its ID."""

        for question in self.questions:

            if question["id"] == question_id:
                return question

        return None

    def get_distribution(self, question_id):
        """Return the distribution for a question."""

        return self.distributions.get(question_id)

    def get_all(self):
        """Return all stored distributions."""

        return self.distributions

    def validate_all(self):
        """
        Validate all currently stored distributions.
        """

        for question_id, distribution in self.distributions.items():

            question = self._find_question(question_id)

            if question is None:
                raise ValueError(
                    f"Question ID {question_id} was not found."
                )

            options = question.get("options", [])

            # Convert the internal dictionary back to the original
            # percentage order for validation.
            percentages = [
                distribution[option]
                for option in options
            ]

            self.set_distribution(
                question_id,
                percentages
            )

        return True