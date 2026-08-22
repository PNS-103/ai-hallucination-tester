from utils.metrics import calculate_summary, category_statistics


def test_scoring():
    evaluations = [
        {"question_id":"FP001","hallucination":True,"severity":5,"confidence":.9,"correctness":"incorrect","status":"success"},
        {"question_id":"FP002","hallucination":False,"severity":0,"confidence":.8,"correctness":"correct","status":"success"},
    ]
    responses = [
        {"question_id":"FP001","latency":1.0,"status":"success"},
        {"question_id":"FP002","latency":3.0,"status":"success"},
    ]
    s = calculate_summary(evaluations, responses)
    assert s["hallucination_rate"] == 50
    assert s["correct_response_rate"] == 50
    assert s["weighted_hallucination_score"] == 50
    assert s["average_latency"] == 2


def test_category_stats():
    evaluations = [{"question_id":"FP001","hallucination":True,"correctness":"incorrect","status":"success"}]
    questions = {"FP001":{"id":"FP001","category":"false_premise"}}
    stats = category_statistics(evaluations, questions)
    assert stats["false_premise"]["hallucination_rate"] == 100
