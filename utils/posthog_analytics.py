from typing import Dict, Tuple

import pandas as pd

from utils.bigquery import run_query

PARAMS_TYPE = Dict[str, Tuple[str, object]]

POSTHOG_EVENTS_TABLE = "`gen-lang-client-0625543859.posthog.Events`"


def fetch_exception_rate_trends(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        SELECT
          DATE(timestamp) AS date,
          COUNTIF(event = '$exception') AS exception_count,
          COUNT(*) AS total_events,
          ROUND(
            SAFE_DIVIDE(COUNTIF(event = '$exception'), COUNT(*)) * 100,
            2
          ) AS exception_rate_percent,
          COUNT(DISTINCT distinct_id) AS total_users,
          COUNT(DISTINCT IF(event = '$exception', distinct_id, NULL)) AS users_with_errors
        FROM {POSTHOG_EVENTS_TABLE}
        WHERE timestamp >= @start_ts
          AND timestamp < @end_ts
        GROUP BY date
        ORDER BY date DESC
    """
    return run_query(sql, params)


def fetch_users_affected_by_errors(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        SELECT
          person_id,
          person.properties.email AS user_email,
          COUNT(*) AS exception_count,
          COUNT(DISTINCT properties.`$exception_type`) AS unique_error_types,
          MIN(timestamp) AS first_error,
          MAX(timestamp) AS last_error,
          DATE_DIFF(DATE(MAX(timestamp)), DATE(MIN(timestamp)), DAY) AS days_with_errors
        FROM {POSTHOG_EVENTS_TABLE}
        WHERE event = '$exception'
          AND timestamp >= @start_ts
          AND timestamp < @end_ts
        GROUP BY person_id, user_email
        ORDER BY exception_count DESC
        LIMIT 100
    """
    return run_query(sql, params)


def fetch_error_distribution_by_type(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        SELECT
          JSON_VALUE(properties, '$."$exception_type"') AS error_type,
          JSON_VALUE(properties, '$."$exception_message"') AS error_message,
          COUNT(*) AS occurrence_count,
          COUNT(DISTINCT distinct_id) AS users_affected,
          COUNT(DISTINCT JSON_VALUE(properties, '$."$session_id"')) AS sessions_affected,
          ROUND(
            AVG(
              CASE
                WHEN JSON_VALUE(properties, '$."$exception_type"') = 'fatal' THEN 3
                WHEN JSON_VALUE(properties, '$."$exception_type"') = 'error' THEN 2
                WHEN JSON_VALUE(properties, '$."$exception_type"') = 'warning' THEN 1
                ELSE 0
              END
            ),
            2
          ) AS avg_severity_score
        FROM {POSTHOG_EVENTS_TABLE}
        WHERE event = '$exception'
          AND timestamp >= @start_ts
          AND timestamp < @end_ts
        GROUP BY error_type, error_message
        ORDER BY occurrence_count DESC
        LIMIT 50
    """
    return run_query(sql, params)


def fetch_web_vitals_metrics(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        WITH base AS (
          SELECT
            DATE(timestamp) AS date,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_LCP_value"') AS FLOAT64) AS lcp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_FCP_value"') AS FLOAT64) AS fcp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_INP_value"') AS FLOAT64) AS inp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_CLS_value"') AS FLOAT64) AS cls_score
          FROM {POSTHOG_EVENTS_TABLE}
          WHERE event = '$web_vitals'
            AND timestamp >= @start_ts
            AND timestamp < @end_ts
        )
        SELECT
          date,
          ROUND(AVG(lcp_ms) / 1000, 2) AS avg_lcp_seconds,
          COUNTIF(lcp_ms / 1000 <= 2.5) AS lcp_good,
          COUNTIF(lcp_ms / 1000 > 2.5 AND lcp_ms / 1000 <= 4.0) AS lcp_needs_improvement,
          COUNTIF(lcp_ms / 1000 > 4.0) AS lcp_poor,
          ROUND(AVG(fcp_ms) / 1000, 2) AS avg_fcp_seconds,
          COUNTIF(fcp_ms / 1000 <= 1.8) AS fcp_good,
          COUNTIF(fcp_ms / 1000 > 1.8 AND fcp_ms / 1000 <= 3.0) AS fcp_needs_improvement,
          COUNTIF(fcp_ms / 1000 > 3.0) AS fcp_poor,
          ROUND(AVG(inp_ms), 2) AS avg_inp_ms,
          COUNTIF(inp_ms <= 200) AS inp_good,
          COUNTIF(inp_ms > 200 AND inp_ms <= 500) AS inp_needs_improvement,
          COUNTIF(inp_ms > 500) AS inp_poor,
          ROUND(AVG(cls_score), 3) AS avg_cls_score,
          COUNTIF(cls_score <= 0.1) AS cls_good,
          COUNTIF(cls_score > 0.1 AND cls_score <= 0.25) AS cls_needs_improvement,
          COUNTIF(cls_score > 0.25) AS cls_poor
        FROM base
        GROUP BY date
        ORDER BY date DESC
    """
    return run_query(sql, params)


def fetch_error_free_session_rate(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        WITH session_errors AS (
          SELECT DISTINCT
            JSON_VALUE(properties, '$."$session_id"') AS session_id
          FROM {POSTHOG_EVENTS_TABLE}
          WHERE event = '$exception'
            AND timestamp >= @start_ts
            AND timestamp < @end_ts
            AND JSON_VALUE(properties, '$."$session_id"') IS NOT NULL
        ),
        all_sessions AS (
          SELECT DISTINCT
            JSON_VALUE(properties, '$."$session_id"') AS session_id
          FROM {POSTHOG_EVENTS_TABLE}
          WHERE timestamp >= @start_ts
            AND timestamp < @end_ts
            AND JSON_VALUE(properties, '$."$session_id"') IS NOT NULL
        )
        SELECT
          CURRENT_DATE() AS report_date,
          COUNT(DISTINCT s.session_id) AS total_sessions,
          COUNT(DISTINCT e.session_id) AS sessions_with_errors,
          COUNT(DISTINCT s.session_id) - COUNT(DISTINCT e.session_id) AS error_free_sessions,
          ROUND(
            SAFE_DIVIDE(
              COUNT(DISTINCT s.session_id) - COUNT(DISTINCT e.session_id),
              COUNT(DISTINCT s.session_id)
            ) * 100,
            2
          ) AS error_free_rate_percent
        FROM all_sessions s
        LEFT JOIN session_errors e
          ON s.session_id = e.session_id
    """
    return run_query(sql, params)


def fetch_rage_clicks(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        SELECT
          DATE(timestamp) AS date,
          JSON_VALUE(properties, '$."$current_url"') AS page_url,
          COUNT(*) AS rageclick_count,
          COUNT(DISTINCT distinct_id) AS users_frustrated,
          COUNT(DISTINCT JSON_VALUE(properties, '$."$session_id"')) AS sessions_with_rageclicks,
          ROUND(
            SAFE_DIVIDE(
              COUNT(*),
              COUNT(DISTINCT JSON_VALUE(properties, '$."$session_id"'))
            ),
            2
          ) AS avg_rageclicks_per_session
        FROM {POSTHOG_EVENTS_TABLE}
        WHERE event = '$rageclick'
          AND timestamp >= @start_ts
          AND timestamp < @end_ts
          AND JSON_VALUE(properties, '$."$session_id"') IS NOT NULL
        GROUP BY date, page_url
        ORDER BY rageclick_count DESC
        LIMIT 50
    """
    return run_query(sql, params)


def fetch_network_connectivity(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        SELECT
          DATE(timestamp) AS date,
          JSON_VALUE(properties, '$."$status"') AS network_status,
          JSON_VALUE(properties, '$."$connection_type"') AS connection_type,
          COUNT(*) AS status_change_count,
          COUNT(DISTINCT distinct_id) AS users_affected,
          COUNT(DISTINCT JSON_VALUE(properties, '$."$session_id"')) AS sessions_affected
        FROM {POSTHOG_EVENTS_TABLE}
        WHERE event = 'network_status_changed'
          AND timestamp >= @start_ts
          AND timestamp < @end_ts
          AND JSON_VALUE(properties, '$."$session_id"') IS NOT NULL
        GROUP BY date, network_status, connection_type
        ORDER BY date DESC, status_change_count DESC
    """
    return run_query(sql, params)


def fetch_performance_percentiles(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        WITH base AS (
          SELECT
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_LCP_value"') AS FLOAT64) / 1000.0 AS lcp_seconds,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_FCP_value"') AS FLOAT64) / 1000.0 AS fcp_seconds,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_INP_value"') AS FLOAT64) AS inp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_CLS_value"') AS FLOAT64) AS cls_score
          FROM {POSTHOG_EVENTS_TABLE}
          WHERE event = '$web_vitals'
            AND timestamp >= @start_ts
            AND timestamp < @end_ts
        ),
        lcp AS (
          SELECT
            'LCP (Largest Contentful Paint)' AS metric_name,
            'seconds' AS unit,
            APPROX_QUANTILES(lcp_seconds, 100)[OFFSET(50)] AS p50,
            APPROX_QUANTILES(lcp_seconds, 100)[OFFSET(75)] AS p75,
            APPROX_QUANTILES(lcp_seconds, 100)[OFFSET(95)] AS p95,
            APPROX_QUANTILES(lcp_seconds, 100)[OFFSET(99)] AS p99
          FROM base
          WHERE lcp_seconds IS NOT NULL
        ),
        fcp AS (
          SELECT
            'FCP (First Contentful Paint)' AS metric_name,
            'seconds' AS unit,
            APPROX_QUANTILES(fcp_seconds, 100)[OFFSET(50)] AS p50,
            APPROX_QUANTILES(fcp_seconds, 100)[OFFSET(75)] AS p75,
            APPROX_QUANTILES(fcp_seconds, 100)[OFFSET(95)] AS p95,
            APPROX_QUANTILES(fcp_seconds, 100)[OFFSET(99)] AS p99
          FROM base
          WHERE fcp_seconds IS NOT NULL
        ),
        inp AS (
          SELECT
            'INP (Interaction to Next Paint)' AS metric_name,
            'milliseconds' AS unit,
            APPROX_QUANTILES(inp_ms, 100)[OFFSET(50)] AS p50,
            APPROX_QUANTILES(inp_ms, 100)[OFFSET(75)] AS p75,
            APPROX_QUANTILES(inp_ms, 100)[OFFSET(95)] AS p95,
            APPROX_QUANTILES(inp_ms, 100)[OFFSET(99)] AS p99
          FROM base
          WHERE inp_ms IS NOT NULL
        ),
        cls AS (
          SELECT
            'CLS (Cumulative Layout Shift)' AS metric_name,
            'score' AS unit,
            APPROX_QUANTILES(cls_score, 100)[OFFSET(50)] AS p50,
            APPROX_QUANTILES(cls_score, 100)[OFFSET(75)] AS p75,
            APPROX_QUANTILES(cls_score, 100)[OFFSET(95)] AS p95,
            APPROX_QUANTILES(cls_score, 100)[OFFSET(99)] AS p99
          FROM base
          WHERE cls_score IS NOT NULL
        )
        SELECT
          metric_name,
          unit,
          ROUND(p50, IF(unit = 'score', 3, 2)) AS p50,
          ROUND(p75, IF(unit = 'score', 3, 2)) AS p75,
          ROUND(p95, IF(unit = 'score', 3, 2)) AS p95,
          ROUND(p99, IF(unit = 'score', 3, 2)) AS p99
        FROM (
          SELECT * FROM lcp
          UNION ALL SELECT * FROM fcp
          UNION ALL SELECT * FROM inp
          UNION ALL SELECT * FROM cls
        )
    """
    return run_query(sql, params)


def fetch_application_logs(params: PARAMS_TYPE) -> pd.DataFrame:
    sql = f"""
        SELECT
          DATE(timestamp) AS date,
          JSON_VALUE(properties, '$.level') AS log_level,
          JSON_VALUE(properties, '$.message') AS log_message,
          COUNT(*) AS log_count,
          COUNT(DISTINCT distinct_id) AS users_affected
        FROM {POSTHOG_EVENTS_TABLE}
        WHERE event = 'log'
          AND timestamp >= @start_ts
          AND timestamp < @end_ts
        GROUP BY date, log_level, log_message
        ORDER BY date DESC, log_count DESC
        LIMIT 100
    """
    return run_query(sql, params)
