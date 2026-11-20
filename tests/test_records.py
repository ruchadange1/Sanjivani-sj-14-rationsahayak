from app.records import count_by, get_by_id, load_records, search


def test_load_records():
    records = load_records()
    assert isinstance(records, list)
    assert len(records) > 0


def test_search_records():
    records = load_records()
    result = search(records, "ration")

    assert isinstance(result, list)


def test_search_no_results():
    records = load_records()
    result = search(records, "xyz123notfound")

    assert result == []


def test_count_by_topic():
    records = load_records()
    result = count_by(records, "topic")

    assert isinstance(result, dict)
    assert len(result) > 0


def test_get_by_id():
    records = load_records()
    record_id = records[0]["id"]

    result = get_by_id(records, record_id)

    assert result is not None
    assert result["id"] == record_id


def test_get_invalid_id():
    records = load_records()

    result = get_by_id(records, -1)

    assert result is None