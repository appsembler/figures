import { trackPromise } from 'react-promise-tracker';
import handleErrors from './handleErrors';

const apiUrl = '/figures/api/course-monthly-metrics';

export default {
  getAllCoursesGeneral: ( parameters = '' ) => {
    return trackPromise(
      fetch((`${apiUrl}/${parameters}`), { credentials: "same-origin" })
        .then(handleErrors)
        .then(response => response.error ? response : response.json())
    )
  },
  getSingleCourseGeneral: ( courseId, parameters = '' ) => {
    return trackPromise(
      fetch((`${apiUrl}/${courseId}/${parameters}`), { credentials: "same-origin" })
        .then(handleErrors)
        .then(response => response.error ? response : response.json())
    )
  },
  getSpecificWithHistory: ( courseId, dataEndpoint, parameters = '' ) => {
    return trackPromise(
      fetch((`${apiUrl}/${courseId}/${dataEndpoint}/${parameters}`), { credentials: "same-origin" })
        .then(handleErrors)
        .then(response => response.error ? response : response.json())
    )
  }
}
