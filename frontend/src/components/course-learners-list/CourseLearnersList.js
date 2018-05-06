import React, { Component } from 'react';
import PropTypes from 'prop-types';
import apiConfig from 'base/apiConfig';
import styles from './_course-learners-list.scss';
import classNames from 'classnames/bind';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/fontawesome-free-solid';

let cx = classNames.bind(styles);

class CourseLearnersList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      displayedData: [],
      displayedUsers: this.props.paginationMaxRows,
      allDataDisplayed: false,
      courseUsersEnrollmentData: [],
    };
    this.fetchCourseUserEnrollmentData = this.fetchCourseUserEnrollmentData.bind(this);
    this.getUserMeta = this.getUserMeta.bind(this);
    this.getUserCourseProgress = this.getUserCourseProgress.bind(this);
    this.paginationLoadMore = this.paginationLoadMore.bind(this);
  }

  fetchCourseUserEnrollmentData = () => {
    fetch(apiConfig.courseEnrollmentsApi + '?course_id=' + this.props.courseId)
      .then(response => response.json())
      .then(json => this.setState({
        courseUsersEnrollmentData: json
      }))
  }

  getUserMeta = (username) => {
    // the following api fetch needs to be updated because it currently throws an auth error from the server
    let userMeta = {};
    fetch(apiConfig.edxUserInfoApi + username)
      .then(response => response.json())
      .then(json => userMeta = json)
    console.log(userMeta);
    return userMeta;
  }

  getUserCourseProgress = (userId) => {
    // this is faux for now since we still don't have this API endpoint
    const fauxUserData = {
      courseProgress: '59%',
      courseCompleted: false,
      dateCompleted: '',
    }
    return fauxUserData;
  }

  paginationLoadMore = () => {
    this.setState({
      displayedUsers: this.state.displayedUsers + this.props.paginationMaxRows
    })
  }

  componentDidMount() {
    this.fetchCourseUserEnrollmentData();
  }


  render() {
    const learnersRender = this.state.courseUsersEnrollmentData.slice(0, this.state.displayedUsers).map((user, index) => {
      const userMeta = this.getUserMeta(user.user.username);
      const userCourseProgress = this.getUserCourseProgress(user.user.id);
      return (
        <li key={index} className={styles['learner-row']}>
          <span className={styles['name']}>{userMeta.name}</span>
          <span className={styles['country']}>{userMeta.country}</span>
          <span className={styles['date-enrolled']}>{user.created.dateEnrolled}</span>
          <span className={styles['course-progress']}>{userCourseProgress.courseProgress}</span>
          <span className={styles['course-completed']}>{userCourseProgress.courseCompleted && <FontAwesomeIcon icon={faCheck} className={styles['completed-icon']} />}</span>
          <span className={styles['date-completed']}>{userCourseProgress.courseCompleted ? userCourseProgress.dateCompleted : '-'}</span>
        </li>
      )
    })

    return (
      <section className={styles['course-learners-list']}>
        <div className={styles['header']}>
          <div className={styles['header-title']}>
            {this.props.listTitle}
          </div>
        </div>
        <div className={cx({ 'stat-card': true, 'span-2': false, 'span-3': false, 'span-4': true, 'learners-table-container': true})}>
          <ul className={styles['learners-table']}>
            <li key="header" className={styles['header-row']}>
              <span className={styles['name']}>Learner</span>
              <span className={styles['country']}>Country</span>
              <span className={styles['date-enrolled']}>Date enrolled</span>
              <span className={styles['course-progress']}>Course progress</span>
              <span className={styles['course-completed']}>Course completed</span>
              <span className={styles['date-completed']}>Date completed</span>
            </li>
            {learnersRender}
          </ul>
          {!this.state.allDataDisplayed && <button className={styles['load-more-button']} onClick={() => this.paginationLoadMore()}>Load more</button>}
        </div>
      </section>
    )
  }
}

CourseLearnersList.defaultProps = {
  listTitle: 'Per learner info:',
  paginationMaxRows: 10,
}

CourseLearnersList.propTypes = {
  listTitle: PropTypes.string,
  paginationMaxRows: PropTypes.number,
  courseId: PropTypes.string,
};

export default CourseLearnersList;
