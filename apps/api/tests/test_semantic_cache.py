from app.services import semantic_cache as sc


def test_vec_bytes_float32_length():
    assert len(sc._vec_bytes([0.1, 0.2, 0.3])) == 12


def test_parse_first_hit_list_shape():
    reply = [1, "cache:analysis:abc", ["payload", '{"x":1}', "dist", "0.05"]]
    payload, dist = sc._parse_first_hit(reply)
    assert payload == '{"x":1}' and dist == 0.05


def test_parse_first_hit_dict_shape():
    reply = {"results": [{"extra_attributes": {"payload": '{"y":2}', "dist": "0.12"}}]}
    payload, dist = sc._parse_first_hit(reply)
    assert payload == '{"y":2}' and dist == 0.12


def test_parse_first_hit_empty():
    assert sc._parse_first_hit([0]) == (None, None)
