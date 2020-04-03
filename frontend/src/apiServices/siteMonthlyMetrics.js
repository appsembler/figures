import { trackPromise } from 'react-promise-tracker';
import handleErrors from './handleErrors';

const apiUrl = '/figures/api/site-monthly-metrics';

export default {
  getGeneral: ( parameters = '' ) => {
    return trackPromise(
      fetch((`${apiUrl}/${parameters}`), { credentials: "same-origin" })
        .then(handleErrors)
        .then(response => response.error ? response : response.json())
    )
  },
  getSpecificWithHistory: ( dataEndpoint, parameters = '' ) => {
    return trackPromise(
      fetch((`${apiUrl}/${dataEndpoint}/${parameters}`), { credentials: "same-origin" })
        .then(handleErrors)
        .then(response => response.error ? response : response.json())
    )
  }
}
