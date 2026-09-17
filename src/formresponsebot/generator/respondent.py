"""Synthetic respondent generation for formresponsebot."""

import random
import re

from .names import SyntheticNameGenerator


class RespondentGenerator:
    """Generate synthetic respondents from configured distributions."""

    def __init__(
        self,
        question_database,
        distributions,
        ollama_client=None,
        name_generator=None,
    ):
        self.question_database = question_database
        self.distributions = distributions
        self.ollama_client = ollama_client
        self.name_generator = (
            name_generator
            or SyntheticNameGenerator()
        )

    # =========================================================
    # OLLAMA
    # =========================================================

    def check_ollama(self):
        """Check whether the configured Ollama client is available."""

        if self.ollama_client is None:
            return False

        try:
            return self.ollama_client.is_available()

        except Exception:
            return False

    def ollama_generate(self, prompt):
        """Generate text using the configured Ollama client."""

        if self.ollama_client is None:
            return None

        try:
            return self.ollama_client.generate(
                prompt
            )

        except Exception:
            return None

    def clean_generated_response(self, response):
        """Clean generated text."""

        if response is None:
            return ""

        response = str(response).strip()

        response = response.strip("\"'")

        response = re.sub(
            r"^(answer|response)\s*:\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        return response.strip()

    # =========================================================
    # TEXT GENERATION
    # =========================================================

    def generate_text_response(
        self,
        question_text,
    ):
        """Generate a natural short-answer response."""

        prompt = f"""
Generate one realistic, natural-sounding survey response.

Survey question:
{question_text}

Requirements:
- Answer the question directly.
- Keep it concise.
- Use first person.
- Sound like a normal survey respondent.
- Do not mention that the response is AI-generated.
- Do not use quotation marks.
"""

        response = self.ollama_generate(
            prompt
        )

        response = self.clean_generated_response(
            response
        )

        if response:
            return response

        return (
            "I have been influenced by "
            "recommendations and discussions "
            "from other people online."
        )

    # =========================================================
    # PERSONAL FIELDS
    # =========================================================

    def is_name_question(self, question_text):
        """Determine whether a question asks for a name."""

        text = question_text.lower()

        return (
            "name" in text
            and "username" not in text
        )

    def is_email_question(self, question_text):
        """Determine whether a question asks for an email."""

        text = question_text.lower()

        return (
            "email" in text
            or "e-mail" in text
        )

    def is_phone_question(self, question_text):
        """Determine whether a question asks for a phone number."""

        text = question_text.lower()

        return (
            "phone" in text
            or "mobile" in text
            or "contact number" in text
        )

    def is_address_question(self, question_text):
        """Determine whether a question asks for an address."""

        text = question_text.lower()

        return (
            "address" in text
            or "location" in text
        )

    def is_identification_question(self, question_text):
        """Determine whether a question asks for identification."""

        text = question_text.lower()

        return (
            "id number" in text
            or "student id" in text
            or "registration number" in text
        )

    def generate_personal_field(
        self,
        question_text,
    ):
        """Generate an appropriate synthetic personal field."""

        if self.is_name_question(
            question_text
        ):
            return self.name_generator.generate()

        # Do not fabricate contact or identification data.
        if self.is_email_question(
            question_text
        ):
            return ""

        if self.is_phone_question(
            question_text
        ):
            return ""

        if self.is_address_question(
            question_text
        ):
            return ""

        if self.is_identification_question(
            question_text
        ):
            return ""

        return None

    # =========================================================
    # DISTRIBUTIONS
    # =========================================================

    def _get_distribution(
        self,
        question_id,
    ):
        """Return the configured distribution."""

        return self.distributions.get(
            question_id
        )

    def sample_from_distribution(
        self,
        distribution,
    ):
        """Sample one option according to percentages."""

        if not distribution:
            return None

        options = list(
            distribution.keys()
        )

        weights = list(
            distribution.values()
        )

        return random.choices(
            options,
            weights=weights,
            k=1,
        )[0]

    def sample_checkbox_response(
        self,
        question,
    ):
        """
        Sample checkbox selections independently.

        Each checkbox option has its own probability.
        """

        question_id = question["id"]

        distribution = self._get_distribution(
            question_id
        )

        if not distribution:
            return []

        selected = []

        for option, percentage in distribution.items():

            probability = (
                float(percentage) / 100
            )

            if random.random() < probability:
                selected.append(
                    option
                )

        # Required checkbox questions cannot be empty.
        if (
            question.get("required", False)
            and not selected
        ):

            selected_option = (
                self.sample_from_distribution(
                    distribution
                )
            )

            if selected_option is not None:
                selected.append(
                    selected_option
                )

        return selected

    # =========================================================
    # QUESTION CLASSIFICATION
    # =========================================================

    def is_structured_question(
        self,
        question_type,
    ):
        """Determine whether a question uses a distribution."""

        return question_type in {
            "multiple_choice",
            "linear_scale",
            "dropdown",
            "checkbox",
        }

    # =========================================================
    # SINGLE RESPONDENT
    # =========================================================

    def generate_single_respondent(
        self,
        respondent_id,
    ):
        """Generate one complete synthetic respondent."""

        respondent = {
            "respondent_id": respondent_id
        }

        # -----------------------------------------------------
        # PASS 1
        # Structured questions and personal fields.
        # -----------------------------------------------------

        for question in self.question_database:

            question_id = question["id"]
            question_text = question["question"]
            question_type = question["type"]

            # -------------------------------------------------
            # Structured questions
            # -------------------------------------------------

            if self.is_structured_question(
                question_type
            ):

                if question_type == "checkbox":

                    answer = (
                        self.sample_checkbox_response(
                            question
                        )
                    )

                else:

                    distribution = (
                        self._get_distribution(
                            question_id
                        )
                    )

                    answer = (
                        self.sample_from_distribution(
                            distribution
                        )
                    )

                respondent[
                    question_id
                ] = answer

                continue

            # -------------------------------------------------
            # Short answer / paragraph
            # -------------------------------------------------

            if question_type in {
                "short_answer",
                "paragraph",
            }:

                personal_answer = (
                    self.generate_personal_field(
                        question_text
                    )
                )

                if personal_answer is not None:

                    respondent[
                        question_id
                    ] = personal_answer

                else:

                    respondent[
                        question_id
                    ] = self.generate_text_response(
                        question_text
                    )

        return respondent

    # =========================================================
    # BATCH GENERATION
    # =========================================================

    def generate(
        self,
        count,
    ):
        """Generate multiple synthetic respondents."""

        respondents = []

        for respondent_id in range(
            1,
            count + 1
        ):

            respondent = (
                self.generate_single_respondent(
                    respondent_id
                )
            )

            respondents.append(
                respondent
            )

        return respondents

    # =========================================================
    # DISTRIBUTION VALIDATION
    # =========================================================

    def calculate_distribution_report(
        self,
        respondents,
    ):
        """
        Compare configured distributions with
        the actual generated responses.

        Returns a list containing:

        - question ID
        - question text
        - question type
        - expected percentages
        - actual percentages
        - actual response counts
        """

        report = []

        total_respondents = len(
            respondents
        )

        if total_respondents == 0:
            return report

        for question in self.question_database:

            question_id = question["id"]
            question_type = question["type"]

            if not self.is_structured_question(
                question_type
            ):
                continue

            expected = self._get_distribution(
                question_id
            )

            if not expected:
                continue

            actual_counts = {
                option: 0
                for option in expected
            }

            # -------------------------------------------------
            # Count generated responses
            # -------------------------------------------------

            for respondent in respondents:

                answer = respondent.get(
                    question_id
                )

                if question_type == "checkbox":

                    if isinstance(
                        answer,
                        list
                    ):

                        for option in answer:

                            if option in actual_counts:

                                actual_counts[
                                    option
                                ] += 1

                else:

                    if answer in actual_counts:

                        actual_counts[
                            answer
                        ] += 1

            # -------------------------------------------------
            # Convert counts to percentages
            # -------------------------------------------------

            actual_percentages = {}

            for option in expected:

                actual_percentages[
                    option
                ] = (
                    actual_counts[option]
                    / total_respondents
                ) * 100

            # -------------------------------------------------
            # Store report
            # -------------------------------------------------

            report.append(
                {
                    "question_id": question_id,
                    "question": question["question"],
                    "type": question_type,
                    "expected": dict(expected),
                    "actual": actual_percentages,
                    "counts": actual_counts,
                }
            )

        return report