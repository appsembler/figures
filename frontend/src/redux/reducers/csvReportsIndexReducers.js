import Immutable from 'immutable';
import { LOAD_CSV_USER_REPORTS_DATA, LOAD_CSV_GRADE_REPORTS_DATA, LOAD_CSV_COURSE_METRICS_REPORTS_DATA } from '../actions/ActionTypes';

const initialState = {
  receivedAt: '',
  csvUserReports: Immutable.List(),
  csvGradeReports: Immutable.List(),
  csvCourseMetrics: Immutable.List(),
}

const cxvReportsIndex = (state = initialState, action) => {
  switch (action.type) {
    case LOAD_CSV_USER_REPORTS_DATA:
      return Object.assign({}, state, {
        receivedAt: action.receivedAt,
        csvUserReports: Immutable.fromJS(action.fetchedData)
      })
    case LOAD_CSV_GRADE_REPORTS_DATA:
      return Object.assign({}, state, {
        receivedAt: action.receivedAt,
        csvGradeReports: Immutable.fromJS(action.fetchedData)
      })
    case LOAD_CSV_COURSE_METRICS_REPORTS_DATA:
      return Object.assign({}, state, {
        receivedAt: action.receivedAt,
        csvCourseMetrics: Immutable.fromJS(action.fetchedData)
      })
    default:
      return state
  }
}

export default cxvReportsIndex
