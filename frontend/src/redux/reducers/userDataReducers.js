import { SET_USER_ID } from '../actions/ActionTypes';

const initialState = {
  userId: '',
}

const userData = (state = initialState, action) => {
  switch (action.type) {
    case SET_USER_ID:
      return Object.assign({}, state, {
        userId: action.userId
      })
    default:
      return state
  }
}

export default userData
