export default function handleErrors(response) {
  const contentType = response.headers.get("content-type");

  if (!response.ok) {
    return {
      error: response.text()
    }
  } else if (contentType && contentType.indexOf("application/json") === -1) {
    return {
      error: 'The response is not valid JSON'
    };
  }
  return response;
}
