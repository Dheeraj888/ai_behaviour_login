from app.ml import feature_vector


def test_feature_vector_has_six_values():
    sample={"typing_duration":1000,"avg_key_interval":120,"backspace_count":1,"mouse_distance":400,"avg_mouse_speed":220,"login_hour":14.5}
    assert feature_vector(sample).shape == (6,)


def test_feature_vector_order_is_stable():
    sample={"typing_duration":1,"avg_key_interval":2,"backspace_count":3,"mouse_distance":4,"avg_mouse_speed":5,"login_hour":6}
    assert feature_vector(sample).tolist() == [1,2,3,4,5,6]
