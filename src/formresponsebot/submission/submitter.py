"""Google Forms submission workflow."""

import time

from selenium.webdriver.common.by import By

from .browser import BrowserManager
from .form_filler import FormFiller


class Submitter:
    """Handle navigation, question matching, and form submission."""

    def __init__(
        self,
        form_url,
        question_database,
        browser_manager=None,
        form_filler=None,
        page_load_wait=2,
        stop_on_failure=False,
        dry_run=True,
    ):
        self.form_url = form_url
        self.question_database = question_database
        self.browser_manager = browser_manager or BrowserManager()
        self.form_filler = form_filler or FormFiller()
        self.page_load_wait = page_load_wait
        self.stop_on_failure = stop_on_failure
        self.dry_run = dry_run

    def find_button(self, browser, possible_texts):
        """Find a Google Forms navigation button by visible text."""

        buttons = browser.find_elements(
            By.CSS_SELECTOR,
            'div[role="button"]'
        )

        possible_texts_lower = [
            text.lower().strip()
            for text in possible_texts
        ]

        for button in buttons:

            try:

                text = button.text.strip().lower()

                if text in possible_texts_lower:

                    return button

            except Exception:
                pass

        return None

    def find_answer_for_question(
        self,
        block,
        respondent,
    ):
        """Match a visible form question with its generated answer."""

        question_text = (
            self.form_filler
            .get_question_text(block)
        )

        if not question_text:
            return None, None

        matched_question = None

        # ---------------------------------------------------------
        # Exact match
        # ---------------------------------------------------------

        for question in self.question_database:

            known_text = (
                question["question"]
                .strip()
            )

            if known_text == question_text.strip():

                matched_question = question

                break

        # ---------------------------------------------------------
        # Partial match fallback
        # ---------------------------------------------------------

        if matched_question is None:

            current_text = (
                question_text
                .lower()
                .strip()
            )

            for question in self.question_database:

                known_text = (
                    question["question"]
                    .lower()
                    .strip()
                )

                if current_text and (
                    current_text in known_text
                    or known_text in current_text
                ):

                    matched_question = question

                    break

        if matched_question is None:

            return None, None

        question_id = matched_question["id"]

        answer = respondent.get(
            question_id
        )

        return matched_question, answer

    def fill_current_page(
        self,
        browser,
        respondent,
    ):
        """
        Fill only questions that are actually visible
        on the current Google Forms page.

        Required questions that are not present on the
        current page are not treated as unresolved.
        """

        blocks = (
            self.form_filler
            .get_question_blocks(browser)
        )

        filled_count = 0

        unresolved = []

        visible_question_ids = set()

        for block in blocks:

            try:

                matched_question, answer = (
                    self.find_answer_for_question(
                        block,
                        respondent,
                    )
                )

                # -------------------------------------------------
                # Ignore blocks that are not actual questions
                # -------------------------------------------------

                if matched_question is None:

                    continue

                question_id = matched_question["id"]

                question_type = matched_question["type"]

                visible_question_ids.add(
                    question_id
                )

                # -------------------------------------------------
                # Fill the visible question
                # -------------------------------------------------

                success = (
                    self.form_filler.fill_question(
                        block,
                        browser,
                        answer,
                        question_type,
                    )
                )

                if success:

                    filled_count += 1

                elif (
                    matched_question.get(
                        "required",
                        False,
                    )
                    and answer not in [None, ""]
                ):

                    unresolved.append(
                        question_id
                    )

            except Exception as error:

                print(
                    f"Question processing error: "
                    f"{error}"
                )

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # We deliberately DO NOT inspect the complete
        # question database here.
        #
        # Only questions actually visible on this page
        # can be unresolved.
        # ---------------------------------------------------------

        return filled_count, unresolved

    def submission_confirmed(
        self,
        browser,
    ):
        """Check whether Google Forms displayed a confirmation."""

        time.sleep(2)

        try:

            page_text = (
                browser
                .find_element(
                    By.TAG_NAME,
                    "body",
                )
                .text
                .lower()
            )

        except Exception:

            return False

        confirmation_phrases = [

            "your response has been recorded",

            "response has been recorded",

            "thank you for your response",

            "your response was recorded",

            "response recorded",

        ]

        return any(
            phrase in page_text
            for phrase in confirmation_phrases
        )

    def submit_one_respondent(
        self,
        respondent,
    ):
        """Submit one generated respondent."""

        respondent_number = (
            respondent["respondent_id"]
        )

        browser = None

        result = {

            "respondent_id":
                respondent_number,

            "generated":
                True,

            "browser_opened":
                False,

            "filled":
                False,

            "submitted":
                False,

            "confirmed":
                False,

            "status":
                "Not started",

            "error":
                "",
        }

        try:

            print(
                f"[{respondent_number:03d}] "
                "Opening NEW Chrome..."
            )

            browser = (
                self.browser_manager
                .create()
            )

            result[
                "browser_opened"
            ] = True

            browser.get(
                self.form_url
            )

            time.sleep(
                self.page_load_wait
            )

            print(
                f"[{respondent_number:03d}] "
                "Form opened."
            )

            page_number = 1

            total_filled = 0

            while True:

                print(
                    f"[{respondent_number:03d}] "
                    f"Processing page {page_number}..."
                )

                filled_count, unresolved = (
                    self.fill_current_page(
                        browser,
                        respondent,
                    )
                )

                total_filled += (
                    filled_count
                )

                if unresolved:

                    print(
                        "⚠️ Required fields not filled: "
                        f"{unresolved}"
                    )

                    result[
                        "status"
                    ] = (
                        "Required field unresolved"
                    )

                    if self.stop_on_failure:

                        return result

                time.sleep(
                    0.5
                )

                # -------------------------------------------------
                # Submit button
                # -------------------------------------------------

                submit_button = (
                    self.find_button(
                        browser,
                        [
                            "Submit",
                            "Submit form",
                        ],
                    )
                )

                if submit_button:

                    if self.dry_run:

                        result[
                            "filled"
                        ] = (
                            total_filled > 0
                        )

                        result[
                            "submitted"
                        ] = False

                        result[
                            "status"
                        ] = (
                            "Dry-run complete — "
                            "Submit button detected"
                        )

                        print(
                            f"🛑 "
                            f"[{respondent_number:03d}] "
                            "DRY RUN: "
                            "Submit button detected."
                        )

                        print(
                            "🛑 Submission was NOT clicked."
                        )

                        print(
                            "👀 Browser will remain "
                            "open for inspection."
                        )

                        return result

                    print(
                        f"[{respondent_number:03d}] "
                        "Submitting..."
                    )

                    try:

                        submit_button.click()

                    except Exception:

                        browser.execute_script(
                            "arguments[0].click();",
                            submit_button,
                        )

                    result[
                        "submitted"
                    ] = True

                    result[
                        "filled"
                    ] = (
                        total_filled > 0
                    )

                    result[
                        "confirmed"
                    ] = (
                        self.submission_confirmed(
                            browser
                        )
                    )

                    if result[
                        "confirmed"
                    ]:

                        result[
                            "status"
                        ] = "Success"

                        print(
                            f"✅ "
                            f"[{respondent_number:03d}] "
                            "Submission confirmed."
                        )

                    else:

                        result[
                            "status"
                        ] = (
                            "Submitted — "
                            "confirmation not detected"
                        )

                        print(
                            f"⚠️ "
                            f"[{respondent_number:03d}] "
                            "Submitted, but confirmation "
                            "was not detected."
                        )

                    break

                # -------------------------------------------------
                # Next button
                # -------------------------------------------------

                next_button = (
                    self.find_button(
                        browser,
                        ["Next"],
                    )
                )

                if next_button is None:

                    result[
                        "status"
                    ] = (
                        "No Next or Submit "
                        "button found"
                    )

                    print(
                        f"❌ "
                        f"[{respondent_number:03d}] "
                        "No Next or Submit button found."
                    )

                    break

                try:

                    next_button.click()

                except Exception:

                    browser.execute_script(
                        "arguments[0].click()",
                        next_button,
                    )

                time.sleep(
                    1.2
                )

                page_number += 1

                if page_number > 50:

                    result[
                        "status"
                    ] = (
                        "Page safety limit reached"
                    )

                    print(
                        f"❌ "
                        f"[{respondent_number:03d}] "
                        "Page safety limit reached."
                    )

                    break

        except Exception as error:

            result[
                "status"
            ] = "Failed"

            result[
                "error"
            ] = str(error)

            print(
                f"❌ "
                f"[{respondent_number:03d}] "
                f"Error: {error}"
            )

        finally:

            if browser is not None:

                if self.dry_run:

                    print(
                        f"[{respondent_number:03d}] "
                        "Chrome left open for inspection."
                    )

                else:

                    self.browser_manager.close(
                        browser
                    )

                    print(
                        f"[{respondent_number:03d}] "
                        "Chrome closed."
                    )

        return result