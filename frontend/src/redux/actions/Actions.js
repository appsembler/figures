import * as types from './ActionTypes';


export const updateReportName = newName => ({
  type: types.UPDATE_REPORT_NAME,
  newName
})

export const updateReportDescription = newDescription => ({
  type: types.UPDATE_REPORT_DESCRIPTION,
  newDescription
})

export const updateReportCards = newCards => ({
  type: types.UPDATE_REPORT_CARDS,
  newCards
})
