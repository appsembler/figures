import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import ReactCSSTransitionReplace from 'react-css-transition-replace';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/header-content-maus/HeaderContentMaus';
import HeaderContentCourse from 'base/components/header-views/header-content-course/HeaderContentCourse';
import HeaderContentReportsList from 'base/components/header-views/header-content-reports-list/HeaderContentReportsList';
import HeaderReport from 'base/components/header-views/header-report/HeaderReport';
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
                    <Route exact path="/figures" component={HeaderContentMaus} />
                    <Route exact path="/figures/reports" component={HeaderContentReportsList} />
                    <Route path="/figures/course/:courseId" render={({ match }) => <HeaderContentCourse courseId={match.params.courseId} />}/>
                    <Route path="/figures/report/:reportId" render={({ match }) => <HeaderReport reportId={match.params.reportId} />}/>
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
                  <Route exact path="/figures" component={DashboardContent} />
                  <Route exact path="/figures/reports" component={ReportsList} />
                  <Route path="/figures/course/:courseId" render={({ match }) => <SingleCourseContent courseId={match.params.courseId} />}/>
                  <Route path="/figures/report/:reportId" render={({ match }) => <SingleReportContent reportId={match.params.reportId} />}/>
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
