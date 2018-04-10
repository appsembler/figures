import { combineReducers } from 'redux';
import { routerReducer } from 'react-router-redux';
import report from './reportReducers';

export default combineReducers({
  report,
  routing: routerReducer
})
