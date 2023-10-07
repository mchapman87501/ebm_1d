from app.model.model import Model


def test_gen_temps() -> None:
    sm_min = 0.1
    sm_max = 2.0
    initial_gat = -60.0
    lat_bands = 9

    m = Model()
    results = list(m.gen_temps(sm_min, sm_max, initial_gat, lat_bands))
    assert len(results) > 0
    for r in results:
        assert sm_min <= r.solar_mult <= sm_max
