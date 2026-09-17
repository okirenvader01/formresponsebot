"""Google Forms scanner for formresponsebot.

The scanner:
1. Opens the Google Form.
2. Scans only the currently visible page.
3. Detects Next or Submit.
4. If Next exists, fills temporary answers and navigates forward.
5. If Submit exists, scans that page and stops WITHOUT submitting.
6. Ignores section headings.
"""

import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..submission.browser import BrowserManager


class GoogleFormScanner:
    """Scan a Google Form page-by-page without submitting it."""

    def __init__(self, form_url):
        self.form_url = form_url
        self.browser_manager = BrowserManager()
        self.driver = None
        self.form_structure = []
        self.question_database = []

    # ---------------------------------------------------------
    # Browser
    # ---------------------------------------------------------

    def create_browser(self):
        """Create a fresh Chrome browser."""
        self.driver = self.browser_manager.create()
        return self.driver

    def close_browser(self):
        """Close the browser safely."""
        if self.driver is not None:
            self.browser_manager.close(self.driver)
            self.driver = None

    # ---------------------------------------------------------
    # Question text
    # ---------------------------------------------------------

    def get_question_text(self, block):
        """Extract the visible text representing a question."""

        selectors = [
            ".M7eMe",
            '[role="heading"]',
            'div[dir="auto"]',
        ]

        for selector in selectors:
            try:
                element = block.find_element(
                    By.CSS_SELECTOR,
                    selector
                )

                text = element.text.strip()

                if text:
                    return text

            except Exception:
                pass

        return ""

    # ---------------------------------------------------------
    # Required detection
    # ---------------------------------------------------------

    def is_required(self, block):
        """Determine whether a question is required."""

        try:
            block.find_element(
                By.CSS_SELECTOR,
                '[aria-label="Required question"]'
            )
            return True

        except Exception:
            pass

        return False

    # ---------------------------------------------------------
    # Options
    # ---------------------------------------------------------

    def get_radio_options(self, block):
        """Return multiple-choice / linear-scale options."""

        options = []

        try:
            elements = block.find_elements(
                By.CSS_SELECTOR,
                '[role="radio"]'
            )

            for element in elements:

                text = (
                    element.get_attribute("aria-label")
                    or element.text
                    or ""
                ).strip()

                if text and text not in options:
                    options.append(text)

        except Exception:
            pass

        return options

    def get_checkbox_options(self, block):
        """Return checkbox options."""

        options = []

        try:
            elements = block.find_elements(
                By.CSS_SELECTOR,
                '[role="checkbox"]'
            )

            for element in elements:

                text = (
                    element.get_attribute("aria-label")
                    or element.text
                    or ""
                ).strip()

                if text and text not in options:
                    options.append(text)

        except Exception:
            pass

        return options

    def get_dropdown_options(self, block):
        """Return dropdown options without permanently changing the form."""

        options = []

        try:
            dropdown = block.find_element(
                By.CSS_SELECTOR,
                '[role="listbox"]'
            )

            dropdown.click()
            time.sleep(0.3)

            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[role="option"]'
            )

            for element in elements:

                text = (
                    element.get_attribute("aria-label")
                    or element.text
                    or ""
                ).strip()

                if text and text not in options:
                    options.append(text)

            # Close dropdown.
            try:
                dropdown.click()
            except Exception:
                pass

        except Exception:
            pass

        return options

    # ---------------------------------------------------------
    # Question type
    # ---------------------------------------------------------

    def detect_question_type(self, block):
        """Detect the type of a Google Forms question."""

        # Multiple choice / linear scale
        try:
            radios = block.find_elements(
                By.CSS_SELECTOR,
                '[role="radio"]'
            )

            if radios:

                options = self.get_radio_options(block)

                if options == ["1", "2", "3", "4", "5"]:
                    return "linear_scale"

                return "multiple_choice"

        except Exception:
            pass

        # Checkbox
        try:
            checkboxes = block.find_elements(
                By.CSS_SELECTOR,
                '[role="checkbox"]'
            )

            if checkboxes:
                return "checkbox"

        except Exception:
            pass

        # Dropdown
        try:
            dropdowns = block.find_elements(
                By.CSS_SELECTOR,
                '[role="listbox"]'
            )

            if dropdowns:
                return "dropdown"

        except Exception:
            pass

        # Paragraph / short answer
        try:
            textareas = block.find_elements(
                By.CSS_SELECTOR,
                "textarea"
            )

            if textareas:
                return "paragraph"

        except Exception:
            pass

        try:
            inputs = block.find_elements(
                By.CSS_SELECTOR,
                "input"
            )

            for field in inputs:

                field_type = (
                    field.get_attribute("type")
                    or ""
                ).lower()

                if field_type not in {
                    "hidden",
                    "radio",
                    "checkbox",
                    "file",
                }:
                    return "short_answer"

        except Exception:
            pass

        # Section headings and other non-question blocks.
        return "unknown"

    # ---------------------------------------------------------
    # Page question blocks
    # ---------------------------------------------------------

    def get_question_blocks(self):
        """Return question blocks currently visible on the page."""

        try:
            return self.driver.find_elements(
                By.CSS_SELECTOR,
                'div[role="listitem"]'
            )

        except Exception:
            return []

    # ---------------------------------------------------------
    # Scan current page
    # ---------------------------------------------------------

    def scan_current_page(self, page_number):
        """Scan only the currently visible page."""

        print(f"Scanning page {page_number}...")

        blocks = self.get_question_blocks()

        page_questions = []

        for block in blocks:

            try:
                question_text = self.get_question_text(block)

                if not question_text:
                    continue

                question_type = self.detect_question_type(block)

                # IMPORTANT:
                # Section headings such as
                # "Engagement & Trust"
                # and "Category & Story"
                # are listitems in Google Forms, but they
                # are NOT questions.
                if question_type == "unknown":
                    continue

                options = []

                if question_type in {
                    "multiple_choice",
                    "linear_scale",
                }:
                    options = self.get_radio_options(block)

                elif question_type == "checkbox":
                    options = self.get_checkbox_options(block)

                elif question_type == "dropdown":
                    options = self.get_dropdown_options(block)

                required = self.is_required(block)

                question = {
                    "question": question_text,
                    "type": question_type,
                    "options": options,
                    "required": required,
                    "page": page_number,
                }

                page_questions.append(question)

            except Exception:
                continue

        print(
            f"Questions found on page {page_number}: "
            f"{len(page_questions)}"
        )

        return page_questions

    # ---------------------------------------------------------
    # Buttons
    # ---------------------------------------------------------

    def find_button(self, possible_texts):
        """Find a visible Google Forms button by its text."""

        try:
            buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                'div[role="button"]'
            )

            possible_texts_lower = [
                text.lower().strip()
                for text in possible_texts
            ]

            for button in buttons:

                try:

                    if not button.is_displayed():
                        continue

                    text = button.text.strip().lower()

                    if text in possible_texts_lower:
                        return button

                except Exception:
                    continue

        except Exception:
            pass

        return None

    def find_submit_button(self):
        """Find the Submit button."""

        return self.find_button(
            [
                "Submit",
                "Submit form",
            ]
        )

    def find_next_button(self):
        """Find the Next button."""

        return self.find_button(
            [
                "Next",
            ]
        )

    # ---------------------------------------------------------
    # Temporary answer filling
    # ---------------------------------------------------------

    def fill_random_multiple_choice(self, block):
        """Select a random radio option."""

        try:
            options = block.find_elements(
                By.CSS_SELECTOR,
                '[role="radio"]'
            )

            if not options:
                return False

            available = [
                option
                for option in options
                if option.is_displayed()
            ]

            if not available:
                return False

            random.choice(available).click()

            return True

        except Exception:
            return False

    def fill_random_checkbox(self, block):
        """Select one or more random checkbox options."""

        try:
            options = block.find_elements(
                By.CSS_SELECTOR,
                '[role="checkbox"]'
            )

            if not options:
                return False

            available = [
                option
                for option in options
                if option.is_displayed()
            ]

            if not available:
                return False

            # Select at least one checkbox.
            selected = random.choice(available)

            try:
                selected.click()
            except Exception:
                return False

            # Randomly select additional options.
            for option in available:

                if option == selected:
                    continue

                if random.random() < 0.25:
                    try:
                        option.click()
                    except Exception:
                        pass

            return True

        except Exception:
            return False

    def fill_random_dropdown(self, block):
        """Select a random dropdown option."""

        try:
            dropdown = block.find_element(
                By.CSS_SELECTOR,
                '[role="listbox"]'
            )

            dropdown.click()

            time.sleep(0.3)

            options = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[role="option"]'
            )

            visible_options = [
                option
                for option in options
                if option.is_displayed()
            ]

            if not visible_options:
                return False

            random.choice(visible_options).click()

            return True

        except Exception:
            return False

    def fill_random_text(self, block):
        """Enter temporary text into a text field."""

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

                if not field.is_displayed():
                    continue

                field.clear()

                field.send_keys(
                    "This is a temporary response."
                )

                return True

        except Exception:
            return False

        return False

    # ---------------------------------------------------------
    # Fill page for navigation
    # ---------------------------------------------------------

    def fill_page_with_random_answers(self):
        """Fill required questions with temporary answers."""

        blocks = self.get_question_blocks()

        for block in blocks:

            try:

                question_type = self.detect_question_type(block)

                # Ignore section headings.
                if question_type == "unknown":
                    continue

                # Only required questions need temporary
                # answers for navigation.
                if not self.is_required(block):
                    continue

                if question_type in {
                    "multiple_choice",
                    "linear_scale",
                }:
                    self.fill_random_multiple_choice(block)

                elif question_type == "checkbox":
                    self.fill_random_checkbox(block)

                elif question_type == "dropdown":
                    self.fill_random_dropdown(block)

                elif question_type in {
                    "short_answer",
                    "paragraph",
                }:
                    self.fill_random_text(block)

            except Exception:
                continue

    # ---------------------------------------------------------
    # Page signature
    # ---------------------------------------------------------

    def get_page_signature(self):
        """Create a signature for the currently visible page."""

        blocks = self.get_question_blocks()

        signature = []

        for block in blocks:

            try:

                text = self.get_question_text(block)

                if text:
                    signature.append(text)

            except Exception:
                pass

        return tuple(signature)

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def go_to_next_page(self, old_signature):
        """Fill temporary answers and move to the next page."""

        print(
            "Using temporary random answers "
            "to navigate..."
        )

        self.fill_page_with_random_answers()

        next_button = self.find_next_button()

        if next_button is None:
            return False

        try:
            next_button.click()

        except Exception:
            try:
                self.driver.execute_script(
                    "arguments[0].click();",
                    next_button
                )

            except Exception:
                return False

        # Wait for Google Forms to update the page.
        try:

            WebDriverWait(
                self.driver,
                10
            ).until(
                lambda driver:
                self.get_page_signature() != old_signature
            )

        except Exception:
            # Some forms can update their DOM without
            # producing a completely different signature.
            time.sleep(1.5)

        time.sleep(1)

        return True

    # ---------------------------------------------------------
    # Main scan
    # ---------------------------------------------------------

    def scan(self):
        """Scan the form page-by-page without submitting."""

        self.form_structure = []
        self.question_database = []

        try:

            print("Opening form...")

            self.create_browser()

            self.driver.get(self.form_url)

            time.sleep(2)

            page_number = 1

            while True:

                # Capture the page signature BEFORE scanning
                # or navigating.
                old_signature = self.get_page_signature()

                page_questions = self.scan_current_page(
                    page_number
                )

                self.form_structure.extend(
                    page_questions
                )

                # -------------------------------------------------
                # IMPORTANT:
                # Check Submit FIRST.
                # If Submit exists, this is the final page.
                # We DO NOT submit the form.
                # -------------------------------------------------

                submit_button = self.find_submit_button()

                if submit_button is not None:

                    print("Submit button detected.")
                    print(
                        "Stopping scan WITHOUT submitting."
                    )

                    break

                # -------------------------------------------------
                # Otherwise look for Next.
                # -------------------------------------------------

                next_button = self.find_next_button()

                if next_button is not None:

                    print("Next button detected.")

                    moved = self.go_to_next_page(
                        old_signature
                    )

                    if not moved:

                        print(
                            "Could not navigate to "
                            "the next page."
                        )

                        break

                    page_number += 1

                    # Safety limit to prevent infinite loops.
                    if page_number > 50:

                        print(
                            "Page safety limit reached."
                        )

                        break

                    continue

                # -------------------------------------------------
                # No Next and no Submit.
                # -------------------------------------------------

                print(
                    "No Next or Submit button found."
                )

                break

            # -----------------------------------------------------
            # Assign IDs only to actual questions.
            # -----------------------------------------------------

            for index, question in enumerate(
                self.form_structure,
                start=1
            ):
                question["id"] = index

            self.question_database = list(
                self.form_structure
            )

            print(
                f"Scan complete. "
                f"Questions found: "
                f"{len(self.question_database)}"
            )

            return self.question_database

        finally:

            self.close_browser()