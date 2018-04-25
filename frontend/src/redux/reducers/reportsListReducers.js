import Immutable from 'immutable';
import { REQUEST_REPORTS_LIST, LOAD_REPORTS_LIST } from '../actions/ActionTypes';

const initialState = {
  isFetching: false,
  receivedAt: '',
  reportsData: Immutable.List(),
}

const reportsList = (state = initialState, action) => {
  switch (action.type) {
    case REQUEST_REPORTS_LIST:
      return Object.assign({}, state, {
        isFetching: true
      })
    case LOAD_REPORTS_LIST:
      return Object.assign({}, state, {
        isFetching: false,
        receivedAt: action.receivedAt,
        reportsData: Immutable.List(action.reportsData),
      })
    default:
      return state
  }
}

export default reportsList
