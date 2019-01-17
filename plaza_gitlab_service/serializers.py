def get_field(obj, field):
    if hasattr(obj, field):
        return getattr(obj, field)
    else:
        return obj[field]


def serialize_object_with_fields(obj, fields):
    serialized = {}
    for field in fields:
        if isinstance(field, tuple):
            name, serializer = field
            print(name, serializer, get_field(obj, name))
            serialized[name] = serializer(get_field(obj, name))
        else:
            serialized[field] = get_field(obj, field)
    return serialized


def serialize_issue(issue):
    return serialize_object_with_fields(issue, ISSUE_FIELDS)


def serialize_user(user):
    print(user)
    return serialize_object_with_fields(user, USER_FIELDS)


def serialize_time(time_stats):
    print(time_stats)
    return serialize_object_with_fields(time_stats, TIME_FIELDS)


def ignore(_):
    return '__skipped'


ISSUE_FIELDS = {
    "id",
    "iid",
    "project_id",
    "title",
    "description",
    "state",
    "created_at",
    "updated_at",
    "closed_at",
    ("closed_by", ignore),
    "milestone",
    "assignees",
    ("author", serialize_user),
    "user_notes_count",
    "upvotes",
    "downvotes",
    "due_date",
    "confidential",
    "discussion_locked",
    "web_url",
    ("time_stats", ignore),
}


USER_FIELDS = {"id", "name", "username", "state", "avatar_url", "web_url"}

TIME_FIELDS = {
    "time_estimate",
    "total_time_spent",
    "human_time_estimate",
    "human_total_time_spent",
}

