import Immutable from 'immutable';

const initialState = {
  reportsList: Immutable.List(),
  currentReportData: {
    reportTitle: '',
    reportAbout: '',
    dateCreated: '',
    reportAuthor: '',
    dataStartDate: '',
    dataEndDate: '',
    reportCarts: Immutable.List(),
  },
}

const reports = (state = initialState, action) => {
  switch (action.type) {
    default:
      return state
  }
}

export default reports
