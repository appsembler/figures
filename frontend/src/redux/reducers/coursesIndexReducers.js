import Immutable from 'immutable';
import { REQUEST_COURSES_INDEX, LOAD_COURSES_INDEX } from '../actions/ActionTypes';

const initialState = {
  isFetching: false,
  receivedAt: '',
  coursesIndex: Immutable.List(),
}

const coursesIndex = (state = initialState, action) => {
  switch (action.type) {
    case REQUEST_COURSES_INDEX:
      return Object.assign({}, state, {
        isFetching: true
      })
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
