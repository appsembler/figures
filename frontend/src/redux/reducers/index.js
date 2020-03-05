import { combineReducers } from 'redux';
import { routerReducer } from 'react-router-redux';
import userData from './userDataReducers';
import report from './reportReducers';
import reportsList from './reportsListReducers';
import generalData from './generalDataReducers';
import csvReportsIndex from './csvReportsIndexReducers';

export default combineReducers({
  userData,
  reportsList,
  report,
  generalData,
  csvReportsIndex,
  routing: routerReducer
})
