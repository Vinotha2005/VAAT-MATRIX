from app.services.quiz_service import generate_quiz, grade_short_answer


def test_generate_quiz_has_all_required_sections():
    quiz = generate_quiz("This lesson explains grammar rules, non terminal symbols, and production rules.")

    questions = quiz["questions"]
    assert len(questions) == 4
    assert {question["type"] for question in questions} == {"mcq", "true_false", "fill_blank", "short_answer"}


def test_short_answer_grading_uses_keywords():
    assert grade_short_answer("The document explains grammar rules and production rules.", ["grammar rules", "production rules"])
    assert not grade_short_answer("It talks about sports.", ["grammar rules", "production rules"])
