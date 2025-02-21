import pytest
import duckdb
import pandas as pd
from pathlib import Path
from message.config import DATA_DIR, QUERIES_DIR


@pytest.fixture
def mock_data():
    """Create a small mock dataset for testing."""
    data = [
        {"session_group": "A","patient_id": "P1", "patient_name": "John Doe", "patient_age": 30, "pain": 2, "fatigue": 3, "therapy_name": "knee", "session_number": 1, "leave_session": None, "quality": 4, "session_is_nok": 0, "quality_reason_other": 1, "quality_reason_exercises": 1,"quality_reason_my_self_personal": 0, "quality_reason_movement_detection": 1, "quality_reason_tablet": 0,"quality_reason_tablet_and_or_motion_trackers": 0,"quality_reason_easy_of_use": 0,"quality_reason_session_speed": 0, "prescribed_repeats": 10, "leave_exercise": "pain", "training_time": 120, "correct_repeats":5, "session_exercise_result_id": 1, "exercise_name": "squat", "wrong_repeats": 5, "exercise_order": 2},
        {"session_group": "A","patient_id": "P1", "patient_name": "John Doe", "patient_age": 30, "pain": 2, "fatigue": 3, "therapy_name": "knee", "session_number": 1, "leave_session": None, "quality": 4, "session_is_nok": 0, "quality_reason_other": 1, "quality_reason_exercises": 1,"quality_reason_my_self_personal": 0, "quality_reason_movement_detection": 1, "quality_reason_tablet": 0,"quality_reason_tablet_and_or_motion_trackers": 0,"quality_reason_easy_of_use": 0,"quality_reason_session_speed": 0, "prescribed_repeats": 15, "leave_exercise": "system_problem", "training_time": 150, "correct_repeats":15, "session_exercise_result_id": 2, "exercise_name": "squat", "wrong_repeats": 5, "exercise_order": 1},
        {"session_group": "B","patient_id": "P2", "patient_name": "Jane Smith", "patient_age": 45, "pain": 5, "fatigue": 6, "therapy_name": "shoulder", "session_number": 2, "leave_session": "discomfort", "quality": 3, "session_is_nok": 1, "quality_reason_other": 0, "quality_reason_exercises": 1,"quality_reason_my_self_personal": 0, "quality_reason_movement_detection": 1, "quality_reason_tablet": 0,"quality_reason_tablet_and_or_motion_trackers": 0,"quality_reason_easy_of_use": 0,"quality_reason_session_speed": 0, "prescribed_repeats": 20, "leave_exercise": None, "training_time": 300, "correct_repeats":10, "session_exercise_result_id": 3, "exercise_name": "lunges", "wrong_repeats": 1, "exercise_order": 1},  
    ]
    return pd.DataFrame(data)



def test_session_transformation(mock_data):
    """Test if session-level aggregation works correctly."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()

    # ✅ Keep only relevant columns for this test
    result = result[[
        "session_group", "patient_id", "patient_name", "pain", "fatigue", "quality", "session_is_nok",
        "quality_reason_other", "quality_reason_exercises"
    ]]

    # ✅ Fix Expected Output
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "patient_id": ["P1", "P2"],
        "patient_name": ["John Doe", "Jane Smith"],
        "pain": [2, 5],
        "fatigue": [3, 6],
        "quality": [4, 3],
        "session_is_nok": [0, 1],
        "quality_reason_other": [1, 0],  # 1 if at least one row has it
        "quality_reason_exercises": [1, 1]  # 1 if at least one row has it
    })

    # ✅ Sort before comparison
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # ✅ Check results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_prescribed_repeats(mock_data):
    """Test if prescribed_repeats is correctly summed."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()
    # ✅ Keep only the relevant columns for this test
    result = result[["session_group", "prescribed_repeats"]]
    # Expected output (Summing prescribed_repeats per session_group)
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "prescribed_repeats": [25, 20]  # A (10+15), B (20)
    })
    
    # ✅ Sort before comparison
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # Check if the output matches the expected results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_training_time(mock_data):
    """Test if training_time is correctly summed per session_group."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()
    # ✅ Keep only the relevant columns for this test
    result = result[["session_group", "training_time"]]

    # Expected output (Summing `training_time` per session_group)
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "training_time": [270, 300]  # A (120+150), B (300)
    })

    # ✅ Sort before comparison
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # Check if the output matches the expected results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_perc_correct_repeats(mock_data):
    """Test if `perc_correct_repeats` is correctly computed per session_group."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()

    # ✅ Keep only the relevant columns for this test
    result = result[["session_group", "perc_correct_repeats"]]

    # Expected output
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "perc_correct_repeats": [0.666666666666666, 0.9090909090909091]
    })

    # ✅ Fix: Sort both DataFrames before comparing
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # Check results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_number_exercises(mock_data):
    """Test if `number_exercises` is correctly counted per session_group."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()

    # ✅ Keep only the relevant columns for this test
    result = result[["session_group", "number_exercises"]]

    # Expected output
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "number_exercises": [2, 1]  # A: 2 exercises, B: 3 exercises
    })

    # ✅ Fix: Sort both DataFrames before comparing
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # Check results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)

def test_number_of_distinct_exercises(mock_data):
    """Test if `number_of_distinct_exercises` is correctly counted per session_group."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()

    # ✅ Keep only the relevant columns for this test
    result = result[["session_group", "number_of_distinct_exercises"]]

    # Expected output
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "number_of_distinct_exercises": [1, 1] 
    })

    # ✅ Fix: Sort both DataFrames before comparing
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # Check results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)

def test_exercise_with_most_incorrect(mock_data):
    """Test if `exercise_with_most_incorrect` is correctly identified."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()

    # ✅ Keep only the relevant columns for this test
    result = result[["session_group", "exercise_with_most_incorrect"]]

    # Expected output
    expected = pd.DataFrame({
        "session_group": ["A", "B"],
        "exercise_with_most_incorrect": ["squat", "lunges"]
    })

    # Sort both DataFrames before comparing
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)
    
    # ✅ Sort before comparison
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # Check results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)

def test_first_exercise_skipped(mock_data):
    """Test if `first_exercise_skipped` is correctly identified per session."""
    
    # Initialize DuckDB
    con = duckdb.connect()

    # Register the mock data as a DuckDB table
    con.register("exercise_results", mock_data)

    # Load the SQL query
    sql_query = Path(QUERIES_DIR, "features.sql").read_text()

    # Run the SQL query
    result = con.execute(sql_query).fetchdf()

    # ✅ Keep only relevant columns for this test
    result = result[["session_group", "first_exercise_skipped"]]

    # ✅ Fix Expected Output
    expected = pd.DataFrame({
        "session_group": ["A","B"],
        "first_exercise_skipped": ["squat", None]  # First skipped exercise in each session
    })

    # ✅ Sort before comparison
    result = result.sort_values(by=["session_group"]).reset_index(drop=True)
    expected = expected.sort_values(by=["session_group"]).reset_index(drop=True)

    # ✅ Check results
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)