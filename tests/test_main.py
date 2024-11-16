import pytest

from google_cloudbuild_visualizer.main import build_graph


@pytest.fixture
def sample_data():
    return {
        "steps": [
            {"id": "step1"},
            {"id": "step2", "waitFor": ["step1"]},
            {"id": "step3", "waitFor": ["step1", "step2"]},
        ]
    }


def test_visualize(sample_data, tmp_path):
    output_file = tmp_path / "test_output.gv"
    build_graph(sample_data, output_file)
    assert output_file.exists()


def test_visualize_invalid_step_id(sample_data):
    sample_data["steps"][0]["id"] = None
    with pytest.raises(Exception):
        build_graph(sample_data, None)
