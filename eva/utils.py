from functools import reduce
import math

def calc_evaluations(evaluations):
    def get_value_rating(criterion):
        return ({
            "Unsatisfactory": 1,
            "Fair": 2,
            "Satisfactory": 3,
            "Very Satisfactory": 4
        }).get(criterion, 0)

    def get_descriptive_rating(criterion):
        if criterion == 1:
            return "Unsatisfactory"
        elif criterion == 2:
            return "Fair"
        elif criterion == 3:
            return "Satisfactory"
        elif criterion == 4:
            return "Very Satisfactory"
        else:
            return "Outlier"

    # NOTE: 4 is 'Very Satisfactory'
    evaluations_total = len(evaluations.get("questions")) * 4

    questions = evaluations.get("questions")
    categories = evaluations.get("categories")
    for x in categories:
        percentage_share = evaluations_total * x.get("percentage") / 100.0
        category_total = len(list(filter(lambda q: q.get("category") == x.get("id"), questions))) * 4
        percentage_ratio = percentage_share / category_total

        # questions
        rating_total = 0.0
        for y in questions:
            if y.get("category") != x.get("id"):
                continue

            answer_rating = get_value_rating(y.get("answer"))
            rating_ratio = answer_rating * percentage_ratio
            y.update({
                'answer_rating': answer_rating,
                'rating_ratio': rating_ratio
            })

            rating_total = rating_total + rating_ratio

        x['percentage_ratio'] = percentage_ratio
        x['rating_total'] = rating_total

    overall_total = sum([x.get("rating_total") for x in categories])

    number_of_questions = len(questions)
    min_descriptive_rating = get_descriptive_rating(math.floor(overall_total / number_of_questions))
    max_descriptive_rating = get_descriptive_rating(math.ceil(overall_total / number_of_questions))

    return {
        "overall_total": overall_total,
        "descriptive_rating": f'{min_descriptive_rating}-{max_descriptive_rating}' if min_descriptive_rating != max_descriptive_rating else min_descriptive_rating,
    }


def get_weighted_value(arr, weight):
    return reduce(lambda total, x: total + x, arr, 0) * weight


# from eva.utils import test_calc_evaluations; test_calc_evaluations()
def test_calc_evaluations():
    calc_evaluations({
        "categories": [
            {"id": 4, "name": "Job Understanding", "percentage": 50},
            {"id": 5, "name": "Job Skills", "percentage": 50},
        ],
        "questions": [
            {"id": 1, "name": "C++", "category": 4, "answer": "Unsatisfactory"},
            {"id": 2, "name": "Flutter", "category": 4, "answer": "Fair"},
            {"id": 3, "name": "Adobe", "category": 5, "answer": "Satisfactory"},
            {"id": 4, "name": "Agile", "category": 5, "answer": "Very Satisfactory"},
        ],
    })
