import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import classNames from 'classnames/bind';
import { connect } from 'react-redux';
import { trackPromise } from 'react-promise-tracker';
import Immutable from 'immutable';
import styles from './_dashboard-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/header-content-maus/HeaderContentMaus';
import BaseStatCard from 'base/components/stat-cards/BaseStatCard';
import apiConfig from 'base/apiConfig';

let cx = classNames.bind(styles);


class DashboardContent extends Component {

  constructor(props) {
    super(props);
    this.state = {
      coursesDetailed: Immutable.List(),
    };
    this.fetchCoursesList = this.fetchCoursesList.bind(this);
  }

  fetchCoursesList = () => {
    trackPromise(
      fetch(apiConfig.coursesDetailed, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          coursesDetailed: Immutable.fromJS(json['results'])
        }))
    )
  }

  componentDidMount() {
    this.fetchCoursesList();
  }

  render() {
    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentMaus
            showHistoryButton
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'dashboard-content': true})}>
          <BaseStatCard
            cardTitle='Registered learners'
            mainValue={this.props.generalData.getIn(['total_site_users', 'current_month'])}
            valueHistory={this.props.generalData.getIn(['total_site_users', 'history'])}
          />
          <BaseStatCard
            cardTitle='Course enrollments'
            mainValue={this.props.generalData.getIn(['total_course_enrollments', 'current_month'])}
            valueHistory={this.props.generalData.getIn(['total_course_enrollments', 'history'])}
          />
          <BaseStatCard
            cardTitle='Course completions'
            mainValue={this.props.generalData.getIn(['total_course_completions', 'current_month'])}
            valueHistory={this.props.generalData.getIn(['total_course_completions', 'history'])}
          />
        </div>
        <div className={cx({ 'container': true, 'functionality-callout': true})}>
          <h3>Quickly access a data for a specific course using the <strong>"Jump to a course"</strong> widget on top, or <strong>Browse all the courses</strong> on the following screen:</h3>
          <NavLink
            to="/figures/courses"
            className={styles['functionality-callout-cta']}
          >
            Browse Courses
          </NavLink>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  generalData: Immutable.fromJS(state.generalData.data)
})

export default connect(
  mapStateToProps,
)(DashboardContent)
