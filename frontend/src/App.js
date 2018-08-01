import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import { connect } from 'react-redux';
import { fetchCoursesIndex, fetchUserIndex, fetchGeneralData } from 'base/redux/actions/Actions';
import ReactCSSTransitionReplace from 'react-css-transition-replace';
import LoadingSpinner from 'base/containers/loading-spinner/LoadingSpinner';
import DashboardContent from 'base/views/DashboardContent';
import MauDetailsContent from 'base/views/MauDetailsContent';
import SingleCourseContent from 'base/views/SingleCourseContent';
import SingleUserContent from 'base/views/SingleUserContent';
import ReportsList from 'base/views/ReportsList';
import SingleReportContent from 'base/views/SingleReportContent';
import 'base/sass/base/_base-overrides.scss';
import styles from 'base/sass/base/_grid.scss';

class App extends Component {

  componentDidMount() {
    this.props.fetchCoursesIndex();
    this.props.fetchUserIndex();
    this.props.fetchGeneralData();
  }

  render() {
    return (
      <LoadingSpinner
        displaySpinner = {!(this.props.activeApiFetches === 0)}
      >
        <main className={styles['layout-root']}>
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
                  <Route path="/figures/course/:courseId" render={({ match }) => <SingleCourseContent courseId={match.params.courseId} />}/>
                  <Route path="/figures/user/:userId" render={({ match }) => <SingleUserContent userId={match.params.userId} />}/>
                  <Route path="/figures/report/:reportId" render={({ match }) => <SingleReportContent reportId={match.params.reportId} />}/>
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
})

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(App)
