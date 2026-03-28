def detect_missing_info(task):
    """
    Returns what is missing in a task
    """
    missing = []

    if task.get("assigned_to") == "Unassigned":
        missing.append("owner")

    if task.get("deadline") == "Not specified":
        missing.append("deadline")

    return missing


def format_tasks_for_display(tasks):
    """
    Prepares tasks for UI display
    """
    formatted = []

    for task in tasks:
        missing = detect_missing_info(task)

        formatted.append({
            "Task": task.get("task"),
            "Owner": task.get("assigned_to"),
            "Deadline": task.get("deadline"),
            "Priority": task.get("priority"),
            "Missing": ", ".join(missing) if missing else "None"
        })

    return formatted


def clean_transcript(text):
    """
    Basic cleaning of transcript
    """
    if not text:
        return ""

    # Remove filler words
    fillers = ["uh", "um", "like", "you know"]
    words = text.split()

    cleaned_words = [w for w in words if w.lower() not in fillers]

    return " ".join(cleaned_words)