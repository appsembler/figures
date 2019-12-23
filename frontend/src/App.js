import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import { connect } from 'react-redux';
import { fetchCoursesIndex, fetchUserIndex, fetchGeneralData, fetchAllCsvReportsData } from 'base/redux/actions/Actions';
import ReactCSSTransitionReplace from 'react-css-transition-replace';
import LoadingSpinner from 'base/containers/loading-spinner/LoadingSpinner';
import DashboardContent from 'base/views/DashboardContent';
import MauDetailsContent from 'base/views/MauDetailsContent';
import SingleCourseContent from 'base/views/SingleCourseContent';
import SingleUserContent from 'base/views/SingleUserContent';
import ReportsList from 'base/views/ReportsList';
import CsvReports from 'base/views/CsvReports';
import SingleReportContent from 'base/views/SingleReportContent';
import 'base/sass/base/_base-overrides.scss';
import styles from 'base/sass/base/_grid.scss';


class App extends Component {

  componentDidMount() {
    this.props.fetchCoursesIndex();
    this.props.fetchUserIndex();
    this.props.fetchGeneralData();
    (process.env.ENABLE_CSV_REPORTS === "enabled") && this.props.fetchAllCsvReportsData();
  }

  render() {

    return (
      <LoadingSpinner>
        <main id="main" className={styles['layout-root']}>
          <Route render={ ({location}) => (
            <ReactCSSTransitionReplace
              transitionName = 'page'
              transitionEnterTimeout = {400}
              transitionLeaveTimeout = {400}
            >
              <div key={this.props.location.pathname}>
                <Switch location={this.props.location}>
                  <Route exact path="/figures" component={DashboardContent} />
                  <Route exact path="/figures/mau-history" component={MauDetailsContent} />
                  <Route exact path="/figures/reports" component={ReportsList} />
                  {(process.env.ENABLE_CSV_REPORTS === "enabled") && <Route exact path="/figures/csv-reports" component={CsvReports} />}
                  <Route path="/figures/course/:courseId" render={({ match }) => <SingleCourseContent courseId={match.params.courseId} />}/>
                  <Route path="/figures/user/:userId" render={({ match }) => <SingleUserContent userId={match.params.userId} />}/>
                  <Route path="/figures/report/:reportId" render={({ match }) => <SingleReportContent reportId={match.params.reportId} />}/>
                  <Route component={DashboardContent} />
                </Switch>
              </div>
            </ReactCSSTransitionReplace>
          )}/>
        </main>
      </LoadingSpinner>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  location: state.routing.location,
  activeApiFetches: state.generalData.activeApiFetches,
})

const mapDispatchToProps = dispatch => ({
  fetchCoursesIndex: () => dispatch(fetchCoursesIndex()),
  fetchUserIndex: () => dispatch(fetchUserIndex()),
  fetchGeneralData: () => dispatch(fetchGeneralData()),
  fetchAllCsvReportsData: () => dispatch(fetchAllCsvReportsData()),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(App)
