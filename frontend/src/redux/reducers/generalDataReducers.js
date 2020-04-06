import { LOAD_ACTIVE_USERS_GENERAL_DATA } from '../actions/ActionTypes';
import { LOAD_SITE_COURSES_GENERAL_DATA } from '../actions/ActionTypes';
import { LOAD_COURSE_ENROLLMENTS_GENERAL_DATA } from '../actions/ActionTypes';
import { LOAD_REGISTERED_USERS_GENERAL_DATA } from '../actions/ActionTypes';
import { LOAD_NEW_USERS_GENERAL_DATA } from '../actions/ActionTypes';
import { LOAD_COURSE_COMPLETIONS_GENERAL_DATA } from '../actions/ActionTypes';

const initialState = {
  activeUsers: {
    "current_month": 0,
    "history": [],
  },
  siteCourses: {
    "current_month": 0,
    "history": [],
  },
  courseEnrollments: {
    "current_month": 0,
    "history": [],
  },
  registeredUsers: {
    "current_month": 0,
    "history": [],
  },
  newUsers: {
    "current_month": 0,
    "history": [],
  },
  courseCompletions: {
    "current_month": 0,
    "history": [],
  }
}

const generalData = (state = initialState, action) => {
  switch (action.type) {
    case LOAD_ACTIVE_USERS_GENERAL_DATA:
      return Object.assign({}, state, {
        activeUsers: action.activeUsersData ? action.activeUsersData : state.activeUsers,
      })
    case LOAD_SITE_COURSES_GENERAL_DATA:
      return Object.assign({}, state, {
        siteCourses: action.siteCoursesData ? action.siteCoursesData : state.siteCourses,
      })
    case LOAD_COURSE_ENROLLMENTS_GENERAL_DATA:
      return Object.assign({}, state, {
        courseEnrollments: action.courseEnrollmentsData ? action.courseEnrollmentsData : state.courseEnrollments,
      })
    case LOAD_REGISTERED_USERS_GENERAL_DATA:
      return Object.assign({}, state, {
        registeredUsers: action.registeredUsersData ? action.registeredUsersData : state.registeredUsers,
      })
    case LOAD_NEW_USERS_GENERAL_DATA:
      return Object.assign({}, state, {
        newUsers: action.newUsersData ? action.newUsersData : state.newUsers,
      })
    case LOAD_COURSE_COMPLETIONS_GENERAL_DATA:
      return Object.assign({}, state, {
        courseCompletions: action.courseCompletionsData ? action.courseCompletionsData : state.courseCompletions,
      })
    default:
      return state
  }
}

export default generalData
