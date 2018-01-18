var React = require('react')

export default class App extends React.Component {

	render() {
		return(
			<h1>Hello, world!</h1>
		);
	}
}

App.defaultProps = {
  debugVerbosity: 0
};