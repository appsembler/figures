import React, { Component } from 'react';
import { Route, NavLink } from 'react-router-dom';
import Dashboard from 'base/views/Dashboard';
import Test from 'base/views/Test';
import 'base/sass/base/_base-overrides.scss';
import styles from 'base/sass/base/_grid.scss';

class App extends Component {
  render() {
    return (
      <main className={styles['layout-root']}>
        <Route exact path="/figures/dashboard" component={Dashboard} />
        <Route exact path="/figures/test" component={Test} />
      </main>
    );
  }
}

export default App;
