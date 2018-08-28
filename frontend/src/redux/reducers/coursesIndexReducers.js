import Immutable from 'immutable';
import { LOAD_COURSES_INDEX } from '../actions/ActionTypes';

const initialState = {
  receivedAt: '',
  coursesIndex: Immutable.List(),
}

const coursesIndex = (state = initialState, action) => {
  switch (action.type) {
    case LOAD_COURSES_INDEX:
      return Object.assign({}, state, {
        isFetching: false,
        receivedAt: action.receivedAt,
        coursesIndex: Immutable.List(action.fetchedData)
      })
    default:
      return state
  }
}

export default coursesIndex
