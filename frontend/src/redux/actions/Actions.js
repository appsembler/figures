import fetch from 'cross-fetch';
import * as types from './ActionTypes';

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
    return fetch(testSingleReportApiURL)
      .then(response => response.json())
      .then(json => dispatch(loadReport(reportId, json)))
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
    return fetch(testReportsListApiURL)
      .then(response => response.json())
      .then(json => dispatch(loadReportsList(json)))
  }
}
