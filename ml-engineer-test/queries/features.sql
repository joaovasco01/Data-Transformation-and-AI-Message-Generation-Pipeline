WITH base AS (
    SELECT
        session_group,
        MIN(patient_id) AS patient_id,
        MIN(patient_name) AS patient_name,  
        MIN(patient_age) AS patient_age,  
        MIN(therapy_name) AS therapy_name,  
        MIN(session_number) AS session_number,  
        MIN(leave_session) AS leave_session,  
        MIN(session_is_nok) AS session_is_nok,  
        MIN(pain) AS pain,  
        MIN(fatigue) AS fatigue,  
        MIN(quality) AS quality,

        -- Aggregate quality reasons
        MAX(quality_reason_movement_detection) AS quality_reason_movement_detection,
        MAX(quality_reason_my_self_personal) AS quality_reason_my_self_personal,
        MAX(quality_reason_other) AS quality_reason_other,
        MAX(quality_reason_exercises) AS quality_reason_exercises,
        MAX(quality_reason_tablet) AS quality_reason_tablet,
        MAX(quality_reason_tablet_and_or_motion_trackers) AS quality_reason_tablet_and_or_motion_trackers,
        MAX(quality_reason_easy_of_use) AS quality_reason_easy_of_use,
        MAX(quality_reason_session_speed) AS quality_reason_session_speed
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

leave_exercise_counts AS (
    SELECT
        session_group,
        COUNT(CASE WHEN leave_exercise IN (
            'system_problem', 'other', 'unable_perform', 'technical_issues', 'difficulty', 'pain', 'tired'
        ) THEN 1 ELSE NULL END) AS leave_exercise_total
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

prescribed_repeats AS (
    SELECT
        session_group,
        SUM(prescribed_repeats) AS prescribed_repeats_total
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

training_time AS (
    SELECT
        session_group,
        SUM(training_time) AS training_time_total
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

perc_correct_repeats AS (
    SELECT
        session_group,
        (SUM(correct_repeats) * 100.0 / NULLIF(SUM(prescribed_repeats), 0)) AS perc_correct_repeats
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

number_exercises AS (
    SELECT
        session_group,
        COUNT(*) AS number_exercises
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

number_of_distinct_exercises AS (
    SELECT
        session_group,
        COUNT(DISTINCT exercise_name) AS number_of_distinct_exercises
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group
),

incorrect_counts AS (
    SELECT
        session_group,
        exercise_name,
        SUM(wrong_repeats) AS total_wrong_repeats
    FROM "./data/exercise_results.parquet"
    GROUP BY session_group, exercise_name
),

ranked_exercises AS (
    SELECT
        session_group,
        exercise_name,
        total_wrong_repeats,
        ROW_NUMBER() OVER (
            PARTITION BY session_group
            ORDER BY total_wrong_repeats DESC
        ) AS rank_incorrect
    FROM incorrect_counts
),

exercise_with_most_incorrect AS (
    SELECT
        session_group,
        exercise_name AS exercise_with_most_incorrect
    FROM ranked_exercises
    WHERE rank_incorrect = 1
),

skipped_exercises AS (
    SELECT
        session_group,
        exercise_name AS first_exercise_skipped,
        exercise_order,
        ROW_NUMBER() OVER (
            PARTITION BY session_group 
            ORDER BY exercise_order ASC
        ) AS row_num
    FROM "./data/exercise_results.parquet"
    WHERE leave_exercise IS NOT NULL
),

all_sessions AS (
    SELECT DISTINCT session_group FROM "./data/exercise_results.parquet"
)

SELECT 
    b.session_group,
    b.patient_id,
    b.patient_name,
    b.patient_age,
    b.therapy_name,
    b.session_number,
    b.leave_session,
    b.session_is_nok,
    b.pain,
    b.fatigue,
    b.quality,

    -- Quality reasons
    b.quality_reason_movement_detection,
    b.quality_reason_my_self_personal,
    b.quality_reason_other,
    b.quality_reason_exercises,
    b.quality_reason_tablet,
    b.quality_reason_tablet_and_or_motion_trackers,
    b.quality_reason_easy_of_use,
    b.quality_reason_session_speed,

    -- Aggregated Features
    COALESCE(l.leave_exercise_total, 0) AS leave_exercise_total,
    COALESCE(pr.prescribed_repeats_total, 0) AS prescribed_repeats_total,
    COALESCE(tt.training_time_total, 0) AS training_time_total,
    COALESCE(pcr.perc_correct_repeats, 0) AS perc_correct_repeats,
    COALESCE(ne.number_exercises, 0) AS number_exercises,
    COALESCE(nd.number_of_distinct_exercises, 0) AS number_of_distinct_exercises,
    COALESCE(inc.exercise_with_most_incorrect, NULL) AS exercise_with_most_incorrect,
    COALESCE(se.first_exercise_skipped, NULL) AS first_exercise_skipped

FROM base b
LEFT JOIN leave_exercise_counts l ON b.session_group = l.session_group
LEFT JOIN prescribed_repeats pr ON b.session_group = pr.session_group
LEFT JOIN training_time tt ON b.session_group = tt.session_group
LEFT JOIN perc_correct_repeats pcr ON b.session_group = pcr.session_group
LEFT JOIN number_exercises ne ON b.session_group = ne.session_group
LEFT JOIN number_of_distinct_exercises nd ON b.session_group = nd.session_group
LEFT JOIN exercise_with_most_incorrect inc ON b.session_group = inc.session_group
LEFT JOIN skipped_exercises se ON b.session_group = se.session_group AND se.row_num = 1;
