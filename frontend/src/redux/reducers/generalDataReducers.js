import { LOAD_GENERAL_DATA } from '../actions/ActionTypes';

const initialState = {
  data: {
    "total_site_users": {
      "current_month":0,
      "history": [
        {"period":"January, 2018","value":0},
        {"period":"February, 2018","value":0},
        {"period":"March, 2018","value":0},
        {"period":"April, 2018","value":0},
        {"period":"May, 2018","value":0},
        {"period":"June, 2018","value":0}
      ]
    },
    "total_course_completions": {
      "current_month": 0,
      "history": [
        {"period":"January, 2018","value":0},
        {"period":"February, 2018","value":0},
        {"period":"March, 2018","value":0},
        {"period":"April, 2018","value":0},
        {"period":"May, 2018","value":0},
        {"period":"June, 2018","value":0}
      ]
    },
    "total_course_enrollments": {
      "current_month":0,
      "history": [
        {"period":"January, 2018","value":0},
        {"period":"February, 2018","value":0},
        {"period":"March, 2018","value":0},
        {"period":"April, 2018","value":0},
        {"period":"May, 2018","value":0},
        {"period":"June, 2018","value":0}
      ]
    },
    "total_site_coures": {
      "current_month":0,
      "history": [
        {"period":"January, 2018","value":0},
        {"period":"February, 2018","value":0},
        {"period":"March, 2018","value":0},
        {"period":"April, 2018","value":0},
        {"period":"May, 2018","value":0},
        {"period":"June, 2018","value":0}
      ]
    },
    "monthly_active_users": {
      "current_month":0,
      "history": [
        {"period":"January, 2018","value":0},
        {"period":"February, 2018","value":0},
        {"period":"March, 2018","value":0},
        {"period":"April, 2018","value":0},
        {"period":"May, 2018","value":0},
        {"period":"June, 2018","value":0}
      ]
    }
  }
}

const generalData = (state = initialState, action) => {
  switch (action.type) {
    case LOAD_GENERAL_DATA:
      return Object.assign({}, state, {
        data: action.generalData
      })
    default:
      return state
  }
}

export default generalData
