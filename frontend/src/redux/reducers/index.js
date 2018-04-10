import { combineReducers } from 'redux';
import { routerReducer } from 'react-router-redux';
import reports from './reportsReducers';

export default combineReducers({
  reports,
  routing: routerReducer
})
