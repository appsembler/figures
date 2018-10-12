import React, { Component } from 'react';
import { connect } from 'react-redux';
import { addActiveApiFetch, removeActiveApiFetch } from 'base/redux/actions/Actions';
import classNames from 'classnames/bind';
import styles from './_single-course-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentCourse from 'base/components/header-views/header-content-course/HeaderContentCourse';
import BaseStatCard from 'base/components/stat-cards/BaseStatCard';
import LearnerStatistics from 'base/components/learner-statistics/LearnerStatistics';
import CourseLearnersList from 'base/components/course-learners-list/CourseLearnersList';
import apiConfig from 'base/apiConfig';

let cx = classNames.bind(styles);

class SingleCourseContent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      courseData: {},
      allLearnersLoaded: true,
      learnersList: [],
      apiFetchMoreLearnersUrl: null
    };

    this.fetchCourseData = this.fetchCourseData.bind(this);
    this.fetchLearnersData = this.fetchLearnersData.bind(this);
    this.setLearnersData = this.setLearnersData.bind(this);
  }

  fetchCourseData = () => {
    this.props.addActiveApiFetch();
    fetch((apiConfig.coursesDetailed + this.props.courseId + '/'), { credentials: "same-origin" })
      .then(response => response.json())
      .then(json => this.setState({
        courseData: json
      }, () => this.props.removeActiveApiFetch()))
  }

  fetchLearnersData = () => {
    this.props.addActiveApiFetch();
    fetch((this.state.apiFetchMoreLearnersUrl === null) ? (apiConfig.learnersDetailed + '?enrolled_in_course_id=' + this.props.courseId) : this.state.apiFetchMoreLearnersUrl, { credentials: "same-origin" })
      .then(response => response.json())
      .then(json => this.setLearnersData(json['results'], json['next']))
  }

  setLearnersData = (results, paginationNext) => {
    const tempLearners = this.state.learnersList.concat(results);
    this.setState ({
      allLearnersLoaded: paginationNext === null,
      learnersList: tempLearners,
      apiFetchMoreLearnersUrl: paginationNext
    }, () => this.props.removeActiveApiFetch())
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
            startDate = {this.state.courseData['start_date']}
            endDate = {this.state.courseData['end_date']}
            courseName = {this.state.courseData['course_name']}
            courseCode = {this.state.courseData['course_code']}
            isSelfPaced = {this.state.courseData['self_paced']}
            learnersEnrolled = {this.state.courseData['learners_enrolled']}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'dashboard-content': true})}>
          <BaseStatCard
            cardTitle='Number of enrolled learners'
            mainValue={this.state.courseData['learners_enrolled'] ? this.state.courseData['learners_enrolled']['current_month'] : 0}
            valueHistory={this.state.courseData['learners_enrolled'] ? this.state.courseData['learners_enrolled']['history'] : []}
          />
          <BaseStatCard
            cardTitle='Average course progress'
            mainValue={this.state.courseData['average_progress'] ? this.state.courseData['average_progress']['current_month'] : 0}
            valueHistory={this.state.courseData['average_progress'] ? this.state.courseData['average_progress']['history'] : []}
          />
          <BaseStatCard
            cardTitle='Average days to complete'
            mainValue={this.state.courseData['average_days_to_complete'] ? this.state.courseData['average_days_to_complete']['current_month'] : 0}
            valueHistory={this.state.courseData['average_days_to_complete'] ? this.state.courseData['average_days_to_complete']['history'] : []}
          />
          <BaseStatCard
            cardTitle='User course completions'
            mainValue={this.state.courseData['users_completed'] ? this.state.courseData['users_completed']['current_month'] : 0}
            valueHistory={this.state.courseData['users_completed'] ? this.state.courseData['users_completed']['history'] : []}
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
  addActiveApiFetch: () => dispatch(addActiveApiFetch()),
  removeActiveApiFetch: () => dispatch(removeActiveApiFetch()),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SingleCourseContent)
