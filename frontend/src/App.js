import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import ReactCSSTransitionReplace from 'react-css-transition-replace';
import DashboardContent from 'base/views/DashboardContent';
import SingleCourseContent from 'base/views/SingleCourseContent';
import ReportsList from 'base/views/ReportsList';
import SingleReportContent from 'base/views/SingleReportContent';
import { history } from './redux/store';
import 'base/sass/base/_base-overrides.scss';
import styles from 'base/sass/base/_grid.scss';

class App extends Component {

  render() {
    return (
      <main className={styles['layout-root']}>
        <Route render={ ({location}) => (
          <ReactCSSTransitionReplace
            transitionName='page'
            transitionEnterTimeout={400}
            transitionLeaveTimeout={400}
          >
            <div key={history.location.pathname}>
              <Switch location={history.location}>
                <Route exact path="/figures" component={DashboardContent} />
                <Route exact path="/figures/reports" component={ReportsList} />
                <Route path="/figures/course/:courseId" render={({ match }) => <SingleCourseContent courseId={match.params.courseId} />}/>
                <Route path="/figures/report/:reportId" render={({ match }) => <SingleReportContent reportId={match.params.reportId} />}/>
              </Switch>
            </div>
          </ReactCSSTransitionReplace>
        )}/>
      </main>
    );
  }
}

export default App;
