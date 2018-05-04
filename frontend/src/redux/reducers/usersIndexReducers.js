import Immutable from 'immutable';
import { REQUEST_USER_INDEX, LOAD_USER_INDEX } from '../actions/ActionTypes';

const initialState = {
  isFetching: false,
  receivedAt: '',
  usersIndex: Immutable.List(),
}

const usersIndex = (state = initialState, action) => {
  switch (action.type) {
    case REQUEST_USER_INDEX:
      return Object.assign({}, state, {
        isFetching: true
      })
    case LOAD_USER_INDEX:
      return Object.assign({}, state, {
        isFetching: false,
        receivedAt: action.receivedAt,
        usersIndex: Immutable.List(action.fetchedData)
      })
    default:
      return state
  }
}

export default usersIndex
