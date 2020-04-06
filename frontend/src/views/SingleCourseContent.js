import React, { Component } from 'react';
import Immutable from 'immutable';
import { connect } from 'react-redux';
import { trackPromise } from 'react-promise-tracker';
import classNames from 'classnames/bind';
import styles from './_single-course-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentCourse from 'base/components/header-views/header-content-course/HeaderContentCourse';
import BaseStatCard from 'base/components/stat-cards/BaseStatCard';
import LearnerStatistics from 'base/components/learner-statistics/LearnerStatistics';
import CourseLearnersList from 'base/components/course-learners-list/CourseLearnersList';
import apiConfig from 'base/apiConfig';
import courseMonthlyMetrics from 'base/apiServices/courseMonthlyMetrics';

let cx = classNames.bind(styles);

class SingleCourseContent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      courseData: Immutable.Map(),
      allLearnersLoaded: true,
      learnersList: Immutable.List(),
      apiFetchMoreLearnersUrl: null
    };
  }

  fetchCourseData = () => {
    trackPromise(
      fetch((apiConfig.coursesGeneral + this.props.courseId + '/'), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          courseData: Immutable.fromJS(json)
        })
      )
    )
  }

  fetchLearnersData = () => {
    trackPromise(
      fetch((this.state.apiFetchMoreLearnersUrl === null) ? (apiConfig.learnersDetailed + '?enrolled_in_course_id=' + this.props.courseId) : this.state.apiFetchMoreLearnersUrl, { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setLearnersData(json['results'], json['next']))
    )
  }

  setLearnersData = (results, paginationNext) => {
    const tempLearners = this.state.learnersList.concat(Immutable.fromJS(results));
    this.setState ({
      allLearnersLoaded: paginationNext === null,
      learnersList: tempLearners,
      apiFetchMoreLearnersUrl: paginationNext
    })
  }

  componentDidMount() {
    this.fetchCourseData();
    this.fetchLearnersData();
  }

  render() {
    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentCourse
            startDate = {this.state.courseData.getIn(['start_date'])}
            endDate = {this.state.courseData.getIn(['end_date'])}
            courseName = {this.state.courseData.getIn(['course_name'])}
            courseCode = {this.state.courseData.getIn(['course_code'])}
            isSelfPaced = {this.state.courseData.getIn(['self_paced'])}
            learnersEnrolled = {this.state.courseData.getIn(['learners_enrolled'])}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'course-quick-links': true})}>
          <span className={styles['course-quick-links__line']}></span>
          <a href={"/courses/" + this.props.courseId} target="_blank" className={styles['course-quick-links__link']}>Open this course in LMS</a>
        </div>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'dashboard-content': true})}>
          <BaseStatCard
            cardTitle='Active users'
            fetchDataKey={'active_users'}
            fetchValueFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
            fetchHistoryFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
          />
          <BaseStatCard
            cardTitle='Number of enrolled learners'
            fetchDataKey={'course_enrollments'}
            fetchValueFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
            fetchHistoryFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
          />
          <BaseStatCard
            cardTitle='Average course progress'
            fetchDataKey={'avg_progress'}
            fetchValueFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
            fetchHistoryFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
            dataType='percentage'
          />
          <BaseStatCard
            cardTitle='Average days to complete'
            fetchDataKey={'avg_days_to_complete'}
            fetchValueFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
            fetchHistoryFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
          />
          <BaseStatCard
            cardTitle='User course completions'
            fetchDataKey={'num_learners_completed'}
            fetchValueFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
            fetchHistoryFunction={(dataKey) => courseMonthlyMetrics.getSpecificWithHistory(this.props.courseId, dataKey)}
          />
          <LearnerStatistics
            learnersData = {this.state.learnersList}
          />
          <CourseLearnersList
            courseId = {this.props.courseId}
            allLearnersLoaded = {this.state.allLearnersLoaded}
            apiFetchMoreLearnersFunction = {this.fetchLearnersData}
            learnersData = {this.state.learnersList}
          />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({

})

const mapDispatchToProps = dispatch => ({

})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SingleCourseContent)
