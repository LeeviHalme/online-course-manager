from modules.db import make_query, make_insert, serialize_to_dict


# get all courses from db
def get_courses(hidden=False):
    # if visible courses were requested
    if not hidden:
        query = make_query("SELECT * FROM courses WHERE NOT is_hidden")
        courses = query.fetchall()
        return courses
    else:
        query = make_query("SELECT * FROM courses")
        courses = query.fetchall()
        return courses


# search courses by their name
def search_courses_by_name(name: str):
    query = make_query(
        "SELECT * FROM courses WHERE UPPER(name) LIKE UPPER(:name)",
        {"name": f"%{name}%"},
    )
    courses = query.fetchall()
    return courses


# find singular course by id
def find_by_id(course_id: str):
    query = make_query(
        "SELECT id, name, short_description, description, is_public, is_hidden FROM courses WHERE id = :course_id",
        {"course_id": course_id},
    )
    return query.fetchone()


# check if user is a participant on a course
# returns boolean status flag
def is_enrolled(course_id: str, user_id: str):
    params = {"course_id": course_id, "user_id": user_id}
    query = make_query(
        "SELECT 1 from participants WHERE user_id = :user_id AND course_id = :course_id",
        params,
    )
    result = query.fetchone()

    if result:
        return True
    else:
        return False


# validate invitation code
# returns boolean status flag
def validate_invitation_code(course_id: str, code: str):
    query = make_query(
        "SELECT invitation_code FROM courses WHERE id = :course_id",
        {"course_id": course_id},
    )
    result = query.fetchone()

    # if course_id was invalid
    if not result:
        return False

    # if code was invalid
    course = serialize_to_dict(result)

    print(course["invitation_code"])

    if course["invitation_code"] != code:
        return False
    else:
        return True


# create a new participant record
def enroll_to_course(course_id: str, user_id: str):
    # insert user into database
    params = {
        "user_id": user_id,
        "course_id": course_id,
    }
    text_query = (
        "INSERT INTO participants (user_id, course_id) VALUES (:user_id, :course_id)"
    )
    make_insert(text_query, params)


# get course materials from db
def get_course_materials(course_id: str):
    query = make_query(
        "SELECT * FROM materials WHERE course_id = :course_id", {"course_id": course_id}
    )
    materials = query.fetchall()
    return materials


# get course exercise count
def get_course_exercise_count(course_id: str) -> int:
    query = make_query(
        "SELECT COUNT(*) FROM exercise_questions WHERE course_id = :course_id",
        {"course_id": course_id},
    )
    result = query.fetchone()
    return result[0]


# get joined exercises questions and answers from db
# TODO: Improve this function's performance
def get_course_exercises(course_id: str):
    query = make_query(
        "SELECT id, question, points, type FROM exercise_questions WHERE course_id = :course_id",
        {"course_id": course_id},
    )
    exercises = query.fetchall()
    to_return = []

    # complete exercises with additional info
    for e in exercises:
        # extra casting to dict required here
        exercise = serialize_to_dict(e)

        # if exercise is multichoise, fetch answers
        if exercise.get("type") == "MULTICHOISE":
            query = make_query(
                "SELECT id, answer type FROM exercise_answers WHERE question_id = :question_id",
                {"question_id": exercise.get("id")},
            )
            exercise["answers"] = query.fetchall()

        # push modified exercise to return array
        to_return.append(exercise)

    return to_return


# get course participants
def get_course_participants(course_id: str):
    query = make_query(
        "SELECT U.id, U.name, U.email, U.type FROM users U LEFT JOIN participants P ON U.id = P.user_id GROUP BY U.id, P.course_id HAVING P.course_id = :course_id",
        {"course_id": course_id},
    )
    return query.fetchall()


# get course invitation code
def get_course_invitation_code(course_id: str):
    query = make_query(
        "SELECT invitation_code FROM courses WHERE id = :course_id",
        {"course_id": course_id},
    )
    return query.fetchone()[0] or None
