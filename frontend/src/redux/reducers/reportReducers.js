import Immutable from 'immutable';
import { UPDATE_REPORT_NAME, UPDATE_REPORT_DESCRIPTION, UPDATE_REPORT_CARDS, REQUEST_REPORT, LOAD_REPORT } from '../actions/ActionTypes';

const initialState = {
  isFetching: false,
  reportId: '',
  receivedAt: '',
  reportName: '',
  reportDescription: '',
  dateCreated: '',
  reportAuthor: '',
  dataStartDate: '',
  dataEndDate: '',
  reportCarts: Immutable.List(),
}

const report = (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_REPORT_NAME:
      return Object.assign({}, state, {
        reportName: action.newName
      })
    case UPDATE_REPORT_DESCRIPTION:
      return Object.assign({}, state, {
        reportDescription: action.newDescription
      })
    case UPDATE_REPORT_CARDS:
      return Object.assign({}, state, {
        reportCarts: action.newCards
      })
    case REQUEST_REPORT:
      return Object.assign({}, state, {
        isFetching: true
      })
    case LOAD_REPORT:
      return Object.assign({}, state, {
        isFetching: false,
        receivedAt: action.receivedAt,
        reportName: action.reportData.reportName,
        reportDescription: action.reportData.reportDescription,
        dateCreated: action.reportData.dateCreated,
        reportAuthor: action.reportData.reportAuthor,
        dataStartDate: action.reportData.dataStartDate,
        dataEndDate: action.reportData.dataEndDate,
        reportCarts: Immutable.List(action.reportData.reportCarts),
      })
    default:
      return state
  }
}

export default report
