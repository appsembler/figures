import React, { Component } from 'react';
import { Route, NavLink } from 'react-router-dom';
import Dashboard from 'base/views/Dashboard';
import Test from 'base/views/Test';

class App extends Component {
  render() {
    return (
      <main className="ef--layout-root">
        <header>
          <NavLink to="/figures/dashboard">Dashboard</NavLink>
          <NavLink to="/figures/test">Test</NavLink>
        </header>
        <Route exact path="/figures/dashboard" component={Dashboard} />
        <Route exact path="/figures/test" component={Test} />
      </main>
    );
  }
}

export default App;
