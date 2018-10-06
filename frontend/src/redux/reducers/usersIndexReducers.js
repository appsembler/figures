import Immutable from 'immutable';
import { LOAD_USER_INDEX } from '../actions/ActionTypes';

const initialState = {
  usersIndex: Immutable.List(),
}

const usersIndex = (state = initialState, action) => {
  switch (action.type) {
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
