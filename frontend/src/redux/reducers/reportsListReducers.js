import Immutable from 'immutable';
import { LOAD_REPORTS_LIST } from '../actions/ActionTypes';

const initialState = {
  reportsData: Immutable.List(),
}

const reportsList = (state = initialState, action) => {
  switch (action.type) {
    case LOAD_REPORTS_LIST:
      return Object.assign({}, state, {
        isFetching: false,
        reportsData: Immutable.List(action.reportsData),
      })
    default:
      return state
  }
}

export default reportsList
