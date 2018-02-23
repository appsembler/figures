import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import ReactCSSTransitionReplace from 'react-css-transition-replace';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/header-content-maus/HeaderContentMaus';
import HeaderContentCourse from 'base/components/header-views/header-content-course/HeaderContentCourse';
import HeaderContentReportsList from 'base/components/header-views/header-content-reports-list/HeaderContentReportsList';
import DashboardContent from 'base/views/DashboardContent';
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
                    <Route exact path="/figures/course" component={HeaderContentCourse} />
                  </Switch>
                </div>
              </ReactCSSTransitionReplace>
            )}/>
          </HeaderAreaLayout>
          <Route render={ ({location}) => (
            <ReactCSSTransitionReplace
              transitionName='page'
              transitionEnterTimeout={400}
              transitionLeaveTimeout={400}
            >
              <div key={history.location.pathname}>
                <Switch location={history.location}>
                  <Route exact path="/figures/dashboard" component={DashboardContent} />
                  <Route exact path="/figures/test" component={HeaderContentReportsList} />
                  <Route exact path="/figures/course" component={HeaderContentCourse} />
                </Switch>
              </div>
            </ReactCSSTransitionReplace>
          )}/>
        </div>
      </main>
    );
  }
}

export default App;
