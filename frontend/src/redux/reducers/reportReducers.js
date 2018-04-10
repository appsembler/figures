import Immutable from 'immutable';
import { UPDATE_REPORT_NAME, UPDATE_REPORT_DESCRIPTION, UPDATE_REPORT_CARDS } from '../actions/ActionTypes';

const initialState = {
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
    default:
      return state
  }
}

export default report
