"""Google Forms question detection and answer filling."""

import time

from selenium.webdriver.common.by import By


class FormFiller:
    """Handle interaction with Google Forms questions."""

    def __init__(self, page_load_wait=2):
        self.page_load_wait = page_load_wait

    def get_question_blocks(self, browser):
        """Return all Google Forms question blocks on the page."""
        return browser.find_elements(
            By.CSS_SELECTOR,
            'div[role="listitem"]'
        )

    def get_question_text(self, block):
        """Extract the question text from a question block."""

        try:
            element = block.find_element(
                By.CSS_SELECTOR,
                ".M7eMe"
            )

            text = element.text.strip()

            if text:
                return text

        except Exception:
            pass

        try:
            element = block.find_element(
                By.CSS_SELECTOR,
                '[role="heading"]'
            )

            text = element.text.strip()

            if text:
                return text

        except Exception:
            pass

        return ""

    def fill_multiple_choice(self, block, answer):
        """Select a Google Forms multiple-choice option."""

        if answer is None:
            return False

        answer = str(answer).strip()

        try:

            options = block.find_elements(
                By.CSS_SELECTOR,
                '[role="radio"]'
            )

            for option in options:

                aria_label = (
                    option.get_attribute("aria-label")
                    or ""
                ).strip()

                option_text = (
                    option.text
                    or ""
                ).strip()

                if (
                    aria_label == answer
                    or option_text == answer
                ):

                    option.click()

                    return True

        except Exception:
            return False

        return False

    def fill_linear_scale(self, block, answer):
        """
        Select a Google Forms linear-scale value.

        Google Forms linear scales use radio-style
        controls, so the answer is matched against
        the radio option's visible text or aria-label.
        """

        if answer is None:
            return False

        answer = str(answer).strip()

        try:

            options = block.find_elements(
                By.CSS_SELECTOR,
                '[role="radio"]'
            )

            for option in options:

                aria_label = (
                    option.get_attribute("aria-label")
                    or ""
                ).strip()

                option_text = (
                    option.text
                    or ""
                ).strip()

                if (
                    aria_label == answer
                    or option_text == answer
                ):

                    option.click()

                    return True

        except Exception:
            return False

        return False

    def fill_checkbox(self, block, answer):
        """Select one or more Google Forms checkbox options."""

        if answer is None:
            return False

        if isinstance(answer, str):

            answers = [answer]

        else:

            try:
                answers = list(answer)

            except Exception:

                answers = [answer]

        answers = [
            str(item).strip()
            for item in answers
        ]

        if not answers:
            return True

        try:

            options = block.find_elements(
                By.CSS_SELECTOR,
                '[role="checkbox"]'
            )

            matched = 0

            for option in options:

                aria_label = (
                    option.get_attribute("aria-label")
                    or ""
                ).strip()

                option_text = (
                    option.text
                    or ""
                ).strip()

                if (
                    aria_label in answers
                    or option_text in answers
                ):

                    # Do not click an option that is
                    # already selected.
                    aria_checked = (
                        option.get_attribute(
                            "aria-checked"
                        )
                        or ""
                    ).lower()

                    if aria_checked != "true":

                        option.click()

                    matched += 1

            return matched > 0

        except Exception:
            return False

    def fill_dropdown(
        self,
        block,
        browser,
        answer,
    ):
        """Select a Google Forms dropdown option."""

        if answer is None:
            return False

        answer = str(answer).strip()

        try:

            dropdown = block.find_element(
                By.CSS_SELECTOR,
                '[role="listbox"]'
            )

            dropdown.click()

            time.sleep(0.3)

            options = browser.find_elements(
                By.CSS_SELECTOR,
                '[role="option"]'
            )

            for option in options:

                option_text = (
                    option.text
                    or ""
                ).strip()

                aria_label = (
                    option.get_attribute(
                        "aria-label"
                    )
                    or ""
                ).strip()

                if (
                    option_text == answer
                    or aria_label == answer
                ):

                    option.click()

                    return True

        except Exception:
            return False

        return False

    def fill_text_field(self, block, answer):
        """Fill a Google Forms short-answer or paragraph field."""

        if answer is None:
            return False

        answer = str(answer)

        try:

            fields = block.find_elements(
                By.CSS_SELECTOR,
                "input, textarea"
            )

            for field in fields:

                field_type = (
                    field.get_attribute("type")
                    or ""
                ).lower()

                if field_type in {
                    "hidden",
                    "radio",
                    "checkbox",
                    "file",
                }:
                    continue

                # Ignore fields that are not displayed.
                try:

                    if not field.is_displayed():
                        continue

                except Exception:
                    pass

                field.clear()

                field.send_keys(answer)

                return True

        except Exception:
            return False

        return False

    def fill_question(
        self,
        block,
        browser,
        answer,
        question_type,
    ):
        """
        Fill a question according to its detected type.
        """

        question_type = (
            str(question_type)
            .lower()
            .strip()
        )

        if question_type in {
            "multiple_choice",
            "multiple choice",
            "radio",
        }:

            return self.fill_multiple_choice(
                block,
                answer,
            )

        if question_type in {
            "linear_scale",
            "linear scale",
        }:

            return self.fill_linear_scale(
                block,
                answer,
            )

        if question_type in {
            "checkbox",
            "checkboxes",
        }:

            return self.fill_checkbox(
                block,
                answer,
            )

        if question_type in {
            "dropdown",
            "drop-down",
        }:

            return self.fill_dropdown(
                block,
                browser,
                answer,
            )

        if question_type in {
            "short_answer",
            "short answer",
            "paragraph",
            "text",
        }:

            return self.fill_text_field(
                block,
                answer,
            )

        return False