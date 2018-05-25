import React, { Component } from 'react';
import PropTypes from 'prop-types';
import {List} from 'immutable';
import moment from 'moment';
import apiConfig from 'base/apiConfig';
import countriesWithCodes from 'base/data/countriesData';
import styles from './_course-learners-list.scss';
import classNames from 'classnames/bind';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/fontawesome-free-solid';

let cx = classNames.bind(styles);

class CourseLearnersList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      displayedUsers: this.props.paginationMaxRows,
      allDataDisplayed: false,
      courseUsersEnrollmentData: [],
      usersData: List(),
    };
    this.fetchCourseUserEnrollmentData = this.fetchCourseUserEnrollmentData.bind(this);
    this.getUserMeta = this.getUserMeta.bind(this);
    this.getUserCourseProgress = this.getUserCourseProgress.bind(this);
    this.paginationLoadMore = this.paginationLoadMore.bind(this);
    this.setUserData = this.setUserData.bind(this);
  }

  fetchCourseUserEnrollmentData = () => {
    fetch(apiConfig.courseEnrollmentsApi + '?course_id=' + this.props.courseId)
      .then(response => response.json())
      // .then(json => this.setState({
      //   courseUsersEnrollmentData: json
      // }))
      .then(json => this.setUserData(json))
  }

  setUserData = (json) => {
    json.map((user, index) => {
      Promise.all([this.getUserMeta(user.user.username), this.getUserCourseProgress(user.user.id)]).then(result => {
        const newUser = {
          username: user.user.username,
          fullname: user.user.fullname,
          userId: user.user.id,
          dateEnrolled: user.created,
          isActive: user['is_active'],
          enrollmentMode: user.mode,
          userMeta: result[0],
          userCourseProgress: result[1]
        }
        this.setState({
          usersData: this.state.usersData.push(newUser)
        })
      })
    })
    console.log(json);
    if (this.props.paginationMaxRows >= json.length) {
      this.setState({
        allDataDisplayed: true,
      })
    }
  }

  getUserMeta = (username) => {
    return fetch(apiConfig.edxUserInfoApi + username, { credentials: "same-origin" })
      .then((response) => response.json())
  }

  getUserCourseProgress = (userId) => {
    // this is faux for now since we still don't have this API endpoint
    const fauxUserData = {
      courseProgress: '59%',
      courseCompleted: false,
      dateCompleted: '',
    }
    return Promise.resolve(fauxUserData);
  }

  paginationLoadMore = () => {
    this.setState({
      displayedUsers: this.state.displayedUsers + this.props.paginationMaxRows,
      allDataDisplayed: ((this.state.displayedUsers + this.props.paginationMaxRows) >= this.state.usersData.size)
    })
  }

  componentDidMount() {
    this.fetchCourseUserEnrollmentData();
  }


  render() {
    const learnersRender = this.state.usersData.slice(0, this.state.displayedUsers).map((user, index) => {

      return (
        <li key={index} className={styles['learner-row']}>
          <span className={styles['name']}>{user.fullname}</span>
          <span className={styles['country']}>{countriesWithCodes[user.userMeta.country]}</span>
          <span className={styles['date-enrolled']}>{moment(user.dateEnrolled).format('LL')}</span>
          <span className={styles['course-progress']}>{user.userCourseProgress.courseProgress}</span>
          <span className={styles['course-completed']}>{user.userCourseProgress.courseCompleted && <FontAwesomeIcon icon={faCheck} className={styles['completed-icon']} />}</span>
          <span className={styles['date-completed']}>{user.userCourseProgress.courseCompleted ? user.userCourseProgress.dateCompleted : '-'}</span>
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
