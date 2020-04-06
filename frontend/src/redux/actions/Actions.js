import fetch from 'cross-fetch';
import * as types from './ActionTypes';
import apiConfig from 'base/apiConfig';
import siteMonthlyMetrics from 'base/apiServices/siteMonthlyMetrics';
import { trackPromise } from 'react-promise-tracker';


// main site metrics related Redux actions

export const loadActiveUsersGeneralData = ( activeUsersData ) => ({
  type: types.LOAD_ACTIVE_USERS_GENERAL_DATA,
  activeUsersData,
  receivedAt: Date.now()
})

export function fetchActiveUsersGeneralData() {
  return dispatch => {
    return siteMonthlyMetrics.getSpecificWithHistory('active_users')
      .then((response) => {
        return response.error ? dispatch(loadActiveUsersGeneralData(false)) : dispatch(loadActiveUsersGeneralData(response['active_users']));
      })
  }
}

export const loadSiteCoursesGeneralData = ( siteCoursesData ) => ({
  type: types.LOAD_SITE_COURSES_GENERAL_DATA,
  siteCoursesData,
  receivedAt: Date.now()
})

export function fetchSiteCoursesGeneralData() {
  return dispatch => {
    return siteMonthlyMetrics.getSpecificWithHistory('site_courses')
      .then((response) => {
        return response.error ? dispatch(loadSiteCoursesGeneralData(false)) : dispatch(loadSiteCoursesGeneralData(response['site_courses']));
      })
  }
}

export const loadCourseEnrollmentsGeneralData = ( courseEnrollmentsData ) => ({
  type: types.LOAD_COURSE_ENROLLMENTS_GENERAL_DATA,
  courseEnrollmentsData,
  receivedAt: Date.now()
})

export function fetchCourseEnrollmentsGeneralData() {
  return dispatch => {
    return siteMonthlyMetrics.getSpecificWithHistory('course_enrollments')
      .then((response) => {
        return response.error ? dispatch(loadCourseEnrollmentsGeneralData(false)) : dispatch(loadCourseEnrollmentsGeneralData(response['course_enrollments']));
      })
  }
}

export const loadRegisteredUsersGeneralData = ( registeredUsersData ) => ({
  type: types.LOAD_REGISTERED_USERS_GENERAL_DATA,
  registeredUsersData,
  receivedAt: Date.now()
})

export function fetchRegisteredUsersGeneralData() {
  return dispatch => {
    return siteMonthlyMetrics.getSpecificWithHistory('registered_users')
      .then((response) => {
        return response.error ? dispatch(loadRegisteredUsersGeneralData(false)) : dispatch(loadRegisteredUsersGeneralData(response['registered_users']));
      })
  }
}

export const loadNewUsersGeneralData = ( newUsersData ) => ({
  type: types.LOAD_NEW_USERS_GENERAL_DATA,
  newUsersData,
  receivedAt: Date.now()
})

export function fetchNewUsersGeneralData() {
  return dispatch => {
    return siteMonthlyMetrics.getSpecificWithHistory('new_users')
      .then((response) => {
        return response.error ? dispatch(loadNewUsersGeneralData(false)) : dispatch(loadNewUsersGeneralData(response['new_users']));
      })
  }
}

export const loadCourseCompletionsGeneralData = ( courseCompletionsData ) => ({
  type: types.LOAD_COURSE_COMPLETIONS_GENERAL_DATA,
  courseCompletionsData,
  receivedAt: Date.now()
})

export function fetchCourseCompletionsGeneralData() {
  return dispatch => {
    return siteMonthlyMetrics.getSpecificWithHistory('course_completions')
      .then((response) => {
        return response.error ? dispatch(loadCourseCompletionsGeneralData(false)) : dispatch(loadCourseCompletionsGeneralData(response['course_completions']));
      })
  }
}



// report related Redux actions

const testSingleReportApiURL = 'https://gist.githubusercontent.com/grozdanowski/1e0f0f4636ceb5c544def8c5b0ff2267/raw/74d72ecd548e21753b9ca2a60dc635347fc01e4b/testReportData.json';
const testReportsListApiURL = 'https://gist.githubusercontent.com/grozdanowski/24f2ef1c6fee3571861e3fc8cc97d4d6/raw/48cfd42f91b3c4c898dbf67db19b8cf8d4051b8b/reportsList.json';

export const setUserId = userId => ({
  type: types.SET_USER_ID,
  userId
})

export const updateReportName = newName => ({
  type: types.UPDATE_REPORT_NAME,
  newName
})

export const updateReportDescription = newDescription => ({
  type: types.UPDATE_REPORT_DESCRIPTION,
  newDescription
})

export const updateReportCards = newCards => ({
  type: types.UPDATE_REPORT_CARDS,
  newCards
})

export const requestReport = reportId => ({
  type: types.REQUEST_REPORT,
  reportId
})

export const loadReport = ( reportId, reportData ) => ({
  type: types.LOAD_REPORT,
  reportId,
  reportData,
  receivedAt: Date.now()
})

export function fetchReport(reportId) {
  return dispatch => {
    dispatch(requestReport(reportId))
    return trackPromise(
      fetch(testSingleReportApiURL, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => dispatch(loadReport(reportId, json)))
    )
  }
}

export const requestReportsList = () => ({
  type: types.REQUEST_REPORTS_LIST,
})

export const loadReportsList = ( reportsData ) => ({
  type: types.LOAD_REPORTS_LIST,
  reportsData,
  receivedAt: Date.now()
})

export function fetchReportsList(userId) {
  return dispatch => {
    dispatch(requestReportsList())
    return trackPromise(
      fetch(testReportsListApiURL, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => dispatch(loadReportsList(json)))
    )
  }
}

export function fetchAllCsvReportsData() {
  return dispatch => {
    dispatch(fetchCsvUserReports());
    dispatch(fetchCsvGradeReports());
    dispatch(fetchCsvCourseMetricsReports());
    return
  }
}

export const loadCsvUserReportsData = ( ReportsData ) => ({
  type: types.LOAD_CSV_USER_REPORTS_DATA,
  fetchedData: ReportsData,
  receivedAt: Date.now()
})

export function fetchCsvUserReports() {
  return dispatch => {
    return trackPromise(
      fetch(apiConfig.reportingCsvReportsApi + '?report_type=LEARNER_DEMOGRAPHICS', { credentials: "same-origin" })
        .then(response => response.json())
        .then (json => dispatch(loadCsvUserReportsData(json)))
    )
  }
}

export const loadCsvGradeReportsData = ( ReportsData ) => ({
  type: types.LOAD_CSV_GRADE_REPORTS_DATA,
  fetchedData: ReportsData,
  receivedAt: Date.now()
})

export function fetchCsvGradeReports() {
  return dispatch => {
    return trackPromise(
      fetch(apiConfig.reportingCsvReportsApi + '?report_type=ENROLLMENT_GRADES', { credentials: "same-origin" })
        .then(response => response.json())
        .then (json => dispatch(loadCsvGradeReportsData(json)))
    )
  }
}

export const loadCsvCourseMetricsReportsData = ( ReportsData ) => ({
  type: types.LOAD_CSV_COURSE_METRICS_REPORTS_DATA,
  fetchedData: ReportsData,
  receivedAt: Date.now()
})

export function fetchCsvCourseMetricsReports() {
  return dispatch => {
    return trackPromise(
      fetch(apiConfig.reportingCsvReportsApi + '?report_type=REPORT_COURSE_METRICS', { credentials: "same-origin" })
        .then(response => response.json())
        .then (json => dispatch(loadCsvCourseMetricsReportsData(json)))
    )
  }
}
