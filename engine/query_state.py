# engine/query_state.py

def init_query_state():
    return {
        "base_question": None,
        "filters": []
    }


def add_filter(state, column, value):
    # ha már van ilyen filter, ne duplikáljuk
    for f in state["filters"]:
        if f["column"] == column:
            f["value"] = value
            return state

    state["filters"].append({"column": column, "value": value})
    return state
