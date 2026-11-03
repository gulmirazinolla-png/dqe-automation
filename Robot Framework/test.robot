*** Settings ***
Library     SeleniumLibrary
Library     helper.py

*** Variables ***
${REPORT_FILE}       ${CURDIR}${/}report.html
${PARQUET_FOLDER}    ${CURDIR}${/}parquet_data${/}facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}       2026-09-27

*** Test Cases ***
HTML Report Table Matches Parquet Dataset
    [Teardown]    Close All Browsers
    ${url}=    Get File Url    ${REPORT_FILE}
    Open Browser    ${url}    edge
    Wait Until Page Contains Element    css:.js-plotly-plot    20s
    ${table}=    Get WebElement    css:.js-plotly-plot
    ${html_df}=    Read Html Table    ${table}
    Log    ${html_df}
    ${parquet_df}=    Read Parquet Data    ${PARQUET_FOLDER}    ${FILTER_DATE}
    Log    ${parquet_df}
    ${diff}=    Compare Dataframes    ${html_df}    ${parquet_df}
    Should Be Empty    ${diff}    msg=HTML table and Parquet data differ:\n${diff}