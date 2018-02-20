import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import ReactCSSTransitionReplace from 'react-css-transition-replace';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/HeaderContentMaus';
import HeaderContentReportsList from 'base/components/header-views/HeaderContentReportsList';
import { history } from './store';
import 'base/sass/base/_base-overrides.scss';
import styles from 'base/sass/base/_grid.scss';

class App extends Component {
  render() {
    return (
      <main className={styles['layout-root']}>
        <div className="ef--layout-root">
          <HeaderAreaLayout location={history.location.pathname}>
            <Route render={ ({location}) => (
              <ReactCSSTransitionReplace
                transitionName='page'
                transitionEnterTimeout={400}
                transitionLeaveTimeout={400}
              >
                <div key={history.location.pathname}>
                  <Switch location={history.location}>
                    <Route exact path="/figures/dashboard" component={HeaderContentMaus} />
                    <Route exact path="/figures/test" component={HeaderContentReportsList} />
                  </Switch>
                </div>
              </ReactCSSTransitionReplace>
            )}/>
          </HeaderAreaLayout>
          <section className="ef--container ef--base-grid-layout">

          </section>
        </div>
      </main>
    );
  }
}

export default App;
