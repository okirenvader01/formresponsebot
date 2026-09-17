"""Command-line interface for formresponsebot."""

from formresponsebot.scanner.form_scanner import GoogleFormScanner
from formresponsebot.scanner.distributions import DistributionManager
from formresponsebot.generator.respondent import RespondentGenerator
from formresponsebot.generator.ollama import OllamaClient
from formresponsebot.submission.submitter import Submitter


def print_header(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_questions(questions):
    print_header("FORM SCAN COMPLETE")

    print()
    print(f"Questions found: {len(questions)}")

    for question in questions:
        print()
        print(
            f"{question['id']}. "
            f"{question['question']}"
        )

        print(
            f"   Type: "
            f"{question['type'].replace('_', ' ').title()}"
        )

        if question.get("options"):
            print("   Options:")

            for option in question["options"]:
                print(f"   - {option}")

        print(
            f"   Required: "
            f"{'Yes' if question.get('required') else 'No'}"
        )


def collect_distributions(questions):
    print_header("RESPONSE DISTRIBUTIONS")

    distribution_manager = DistributionManager(questions)

    for question in questions:

        question_type = question["type"]
        options = question.get("options", [])

        if question_type not in {
            "multiple_choice",
            "linear_scale",
            "dropdown",
            "checkbox",
        }:
            continue

        print()
        print("-" * 70)
        print(
            f"Question {question['id']}: "
            f"{question['question']}"
        )
        print(
            f"Type: "
            f"{question_type.replace('_', ' ').title()}"
        )
        print("-" * 70)

        if question_type == "checkbox":

            print(
                "Enter the percentage of respondents "
                "who should select each option."
            )
            print()
            print("IMPORTANT:")
            print(
                "Checkbox percentages are independent."
            )
            print(
                "They do NOT need to total 100%."
            )

        else:

            print(
                "Enter the percentage distribution."
            )
            print(
                "The total MUST equal 100%."
            )

        percentages = []

        for option in options:

            while True:

                try:

                    value = float(
                        input(f"{option}: ")
                    )

                    if value < 0 or value > 100:

                        print(
                            "Please enter a value "
                            "between 0 and 100."
                        )

                        continue

                    percentages.append(value)

                    break

                except ValueError:

                    print(
                        "Please enter a valid number."
                    )

        while True:

            try:

                distribution_manager.set_distribution(
                    question["id"],
                    percentages,
                )

                break

            except ValueError as error:

                print()
                print(f"ERROR: {error}")
                print()

                percentages = []

                print(
                    "Please enter the percentages "
                    "again for this question."
                )

                for option in options:

                    while True:

                        try:

                            value = float(
                                input(f"{option}: ")
                            )

                            if value < 0 or value > 100:

                                print(
                                    "Please enter a value "
                                    "between 0 and 100."
                                )

                                continue

                            percentages.append(value)

                            break

                        except ValueError:

                            print(
                                "Please enter a valid number."
                            )

    distribution_manager.validate_all()

    print()
    print("=" * 70)
    print("DISTRIBUTIONS SAVED SUCCESSFULLY")
    print("=" * 70)

    return distribution_manager.get_all()


def print_distribution_report(report, total):

    print_header("GENERATION DISTRIBUTION REPORT")

    for data in report:

        print()
        print("-" * 70)

        print(
            f"Question {data['question_id']}: "
            f"{data['question']}"
        )

        print(
            f"Type: "
            f"{data['type'].replace('_', ' ').title()}"
        )

        print()

        print(
            f"{'Option':<35}"
            f"{'Expected':>12}"
            f"{'Actual':>12}"
            f"{'Count':>10}"
        )

        print("-" * 69)

        for option in data["expected"]:

            expected = data["expected"].get(
                option,
                0,
            )

            actual = data["actual"].get(
                option,
                0,
            )

            count = data["counts"].get(
                option,
                0,
            )

            print(
                f"{option:<35}"
                f"{expected:>11.1f}%"
                f"{actual:>11.1f}%"
                f"{count:>10}"
            )

    print()
    print("-" * 70)
    print(
        f"Report based on "
        f"{total} generated respondents."
    )
    print("-" * 70)


def print_generated_respondents(
    respondents,
    questions,
):

    print_header("GENERATED RESPONDENTS")

    for respondent in respondents:

        respondent_id = respondent["respondent_id"]

        print()
        print(f"Respondent {respondent_id}")
        print("-" * 70)

        for question in questions:

            question_id = question["id"]

            if question_id not in respondent:
                continue

            answer = respondent[question_id]

            print(question["question"])
            print(f"  → {answer}")


def print_submission_results(results):

    print_header("SUBMISSION RESULTS")

    successful = 0
    failed = 0

    for result in results:

        print()
        print("-" * 70)

        print(
            f"Respondent: "
            f"{result['respondent_id']}"
        )

        print(
            f"Browser opened: "
            f"{result['browser_opened']}"
        )

        print(
            f"Fields filled: "
            f"{result['filled']}"
        )

        print(
            f"Submitted: "
            f"{result['submitted']}"
        )

        print(
            f"Confirmed: "
            f"{result['confirmed']}"
        )

        print(
            f"Status: "
            f"{result['status']}"
        )

        if result.get("error"):

            print(
                f"Error: "
                f"{result['error']}"
            )

        if (
            result["submitted"]
            and result["confirmed"]
        ):

            successful += 1

        else:

            failed += 1

    print()
    print("=" * 70)
    print("SUBMISSION SUMMARY")
    print("=" * 70)

    print()
    print(
        f"Total generated: "
        f"{len(results)}"
    )

    print(
        f"Successfully submitted and confirmed: "
        f"{successful}"
    )

    print(
        f"Not successfully confirmed: "
        f"{failed}"
    )


def main():

    print_header("FORM RESPONSE BOT")

    form_url = input(
        "Enter the Google Forms URL: "
    ).strip()

    if not form_url:

        print("No form URL provided.")

        return

    print()
    print("Starting form scanner...")
    print()

    scanner = GoogleFormScanner(form_url)

    try:

        questions = scanner.scan()

    except Exception as error:

        print()
        print(
            f"Scanner failed: {error}"
        )

        return

    print_questions(questions)

    print()

    while True:

        try:

            response_count = int(
                input(
                    "How many synthetic responses "
                    "do you want to create? "
                )
            )

            if response_count <= 0:

                print(
                    "Please enter a number greater than 0."
                )

                continue

            break

        except ValueError:

            print(
                "Please enter a valid whole number."
            )

    print()
    print(
        f"You requested "
        f"{response_count} synthetic responses."
    )

    distributions = collect_distributions(
        questions
    )

    print_header(
        "GENERATING SYNTHETIC RESPONSES"
    )

    ollama_client = OllamaClient(
        base_url="http://localhost:11434",
        model="llama3.2:3b",
    )

    if ollama_client.is_available():

        print()
        print(
            "Ollama detected successfully."
        )

        print(
            "Model: llama3.2:3b"
        )

    else:

        print()
        print(
            "WARNING: Ollama is not available."
        )

        print(
            "Open-ended responses will use "
            "the generator fallback."
        )

    generator = RespondentGenerator(
        question_database=questions,
        distributions=distributions,
        ollama_client=ollama_client,
    )

    respondents = []

    for respondent_number in range(
        1,
        response_count + 1,
    ):

        print(
            f"[{respondent_number:03d}] "
            "Generating respondent..."
        )

        try:

            respondent = (
                generator.generate_single_respondent(
                    respondent_number
                )
            )

            respondents.append(
                respondent
            )

            print(
                f"✅ [{respondent_number:03d}] "
                "Respondent generated."
            )

        except Exception as error:

            print(
                f"❌ [{respondent_number:03d}] "
                f"Generation failed: {error}"
            )

    print()
    print_header(
        "RESPONDENT GENERATION COMPLETE"
    )

    print()
    print(
        f"Requested: {response_count}"
    )

    print(
        f"Successfully generated: "
        f"{len(respondents)}"
    )

    if not respondents:

        print()
        print(
            "No respondents were generated."
        )

        return

    validator_generator = RespondentGenerator(
        question_database=questions,
        distributions=distributions,
    )

    distribution_report = (
        validator_generator
        .calculate_distribution_report(
            respondents
        )
    )

    print_distribution_report(
        distribution_report,
        len(respondents),
    )

    print_generated_respondents(
        respondents,
        questions,
    )

    print()
    print("=" * 70)
    print("GENERATION PIPELINE COMPLETE")
    print("=" * 70)

    # ---------------------------------------------------------
    # ACTUAL SUBMISSION
    # ---------------------------------------------------------

    print()
    print("Starting submission...")
    print()

    submitter = Submitter(
        form_url=form_url,
        question_database=questions,
        dry_run=False,
    )

    submission_results = []

    for respondent in respondents:

        respondent_number = (
            respondent["respondent_id"]
        )

        print()
        print(
            f"[{respondent_number:03d}] "
            "Submitting respondent..."
        )

        try:

            result = (
                submitter.submit_one_respondent(
                    respondent
                )
            )

            submission_results.append(
                result
            )

        except Exception as error:

            submission_results.append(
                {
                    "respondent_id": respondent_number,
                    "generated": True,
                    "browser_opened": False,
                    "filled": False,
                    "submitted": False,
                    "confirmed": False,
                    "status": "Failed",
                    "error": str(error),
                }
            )

            print(
                f"❌ [{respondent_number:03d}] "
                f"Submission failed: {error}"
            )

    print_submission_results(
        submission_results
    )

    print()
    print("=" * 70)
    print("FORM RESPONSE BOT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()