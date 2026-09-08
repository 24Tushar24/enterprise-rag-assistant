import json
import re
from app.services.rag_service import RAGService

def normalize_text(text):
    text = text.lower()

    # Normalize different hyphen characters
    text = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2212]", "-", text)


    replacements = {
        "two": "2",
        "three": "3",
        "four": "4",
        "work-from-home": "wfh",
        "work-from-home": "wfh",
        "work from home": "wfh",
        "from home": "wfh",
        "per calendar year": "per year",
        "approved": "approval", 
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())

def load_eval_cases():
    with open("tests/eval_cases.json", "r", encoding="utf-8") as file:
        return json.load(file)


def check_answer_correctness(expected_facts, actual_answer):
    actual = normalize_text(actual_answer)

    # Abstention case
    if not expected_facts:
        return "i don't have enough information" in actual

    for fact in expected_facts:

        fact_type = fact["type"]

        # Numeric fact
        if fact_type == "number":
            value = str(fact["value"])
            unit = normalize_text(fact["unit"])

            if value not in actual:
                return False

            if unit not in actual:
                return False

            if "keyword" in fact:
                keyword = normalize_text(fact["keyword"])
                if keyword not in actual:
                    return False

        # Keyword fact
        elif fact_type == "keyword":
            value = normalize_text(fact["value"])

            if value not in actual:
                return False

        else:
            return False

    return True


def check_citation_correctness(expected_document, actual_citations):
    if expected_document is None:
        return len(actual_citations) == 0

    for citation in actual_citations:
        if citation["filename"] == expected_document:
            return True

    return False


def run_evals():
    rag_service = RAGService()
    eval_cases = load_eval_cases()

    total_cases = len(eval_cases)
    passed_cases = 0

    for case in eval_cases:

        print(f"\nRunning: {case['id']}")
        print(f"Question: {case['question']}")

        actual_result = rag_service.answer(case["question"], request_id=f"eval_{case['id']}")

        answer_pass = check_answer_correctness(
            case["expected_facts"],
            actual_result["answer"],
        )

        citation_pass = check_citation_correctness(
            case["expected_document"],
            actual_result["citations"],
        )

        case_pass = answer_pass and citation_pass

        if case_pass:
            passed_cases += 1

        print(f"Expected: {case['expected_facts']}")
        print(f"Actual: {actual_result['answer']}")
        print(f"Citations: {actual_result['citations']}")

        print(f"Answer Correctness: {'PASS' if answer_pass else 'FAIL'}")
        print(f"Citation Correctness: {'PASS' if citation_pass else 'FAIL'}")

        print(f"Overall: {'PASS' if case_pass else 'FAIL'}")

    accuracy = (passed_cases / total_cases) * 100

    print("\n==============================")
    print("EVALUATION SUMMARY")
    print("==============================")
    print(f"Total Cases: {total_cases}")
    print(f"Passed: {passed_cases}")
    print(f"Failed: {total_cases - passed_cases}")
    print(f"Accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    run_evals()