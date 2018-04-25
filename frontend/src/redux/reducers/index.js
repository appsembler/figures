import { combineReducers } from 'redux';
import { routerReducer } from 'react-router-redux';
import userData from './userDataReducers';
import report from './reportReducers';
import reportsList from './reportsListReducers';

export default combineReducers({
  userData,
  reportsList,
  report,
  routing: routerReducer
})
