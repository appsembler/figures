import fetch from 'cross-fetch';
import * as types from './ActionTypes';
import apiConfig from 'base/apiConfig';
import { trackPromise } from 'react-promise-tracker';

// course index data related Redux actions

export const loadCoursesIndex = ( coursesData ) => ({
  type: types.LOAD_COURSES_INDEX,
  fetchedData: coursesData,
  receivedAt: Date.now()
})

export function fetchCoursesIndex () {
  return dispatch => {
    return trackPromise(
      fetch(apiConfig.coursesGeneral, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => dispatch(loadCoursesIndex(json['results'])))
    )
  }
}


// user index data related Redux actions

export const loadUserIndex = ( coursesData ) => ({
  type: types.LOAD_USER_INDEX,
  fetchedData: coursesData,
  receivedAt: Date.now()
})

export function fetchUserIndex () {
  return dispatch => {
    return trackPromise(
      fetch(apiConfig.learnersGeneral, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => dispatch(loadUserIndex(json.results)))
    )
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

export const loadGeneralData = ( generalData ) => ({
  type: types.LOAD_GENERAL_DATA,
  generalData,
  receivedAt: Date.now()
})

export function fetchGeneralData() {
  return dispatch => {
    return trackPromise(
      fetch(apiConfig.generalSiteMetrics, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => dispatch(loadGeneralData(json)))
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
