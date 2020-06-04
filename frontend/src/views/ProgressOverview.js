import React, { Component } from 'react';
import Immutable from 'immutable';
import { Link } from 'react-router-dom';
import apiConfig from 'base/apiConfig';
import { trackPromise } from 'react-promise-tracker';
import styles from './_progress-overview-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentStatic from 'base/components/header-views/header-content-static/HeaderContentStatic';
import Paginator from 'base/components/layout/Paginator';
import ListSearch from 'base/components/inputs/ListSearch';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck, faAngleDoubleUp, faAngleDoubleDown } from '@fortawesome/free-solid-svg-icons';

import classNames from 'classnames/bind';
let cx = classNames.bind(styles);


class ProgressOverview extends Component {
  constructor(props) {
    super(props);

    this.state = {
      coursesIndex: [],
      coursesList: [],
      learnersList: [],
      selectedCourses: [],
      perPage: 20,
      count: 0,
      pages: 0,
      currentPage: 1,
      searchQuery: '',
      ordering: 'profile__name',
    };

    this.getUsers = this.getUsers.bind(this);
    this.getCourses = this.getCourses.bind(this);
    this.setCoursesIndex = this.setCoursesIndex.bind(this);
    this.setPerPage = this.setPerPage.bind(this);
    this.setSearchQuery = this.setSearchQuery.bind(this);
    this.setOrdering = this.setOrdering.bind(this);
    this.constructApiUrl = this.constructApiUrl.bind(this);
  }

  constructApiUrl(rootUrl, searchQuery, orderingType, perPageLimit, resultsOffset) {
    let requestUrl = rootUrl;
    // add search term
    requestUrl += '?search=' + searchQuery;
    // add ordering
    requestUrl += '&ordering=' + orderingType;
    // add results per page limit
    requestUrl += '&limit=' + perPageLimit;
    // add results offset
    requestUrl += '&offset=' + resultsOffset;
    // return
    return requestUrl;
  }

  getCourses() {
    const requestUrl = apiConfig.coursesIndex + '?limit=1000';
    trackPromise(
      fetch((requestUrl), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setCoursesIndex(json['results']))
    )
  }

  setCoursesIndex(courses) {
    let coursesIndex = {};
    const coursesList = courses.map((course, index) => {
      coursesIndex[course['id']] = course;
      return course['id'];
    })
    this.setState({
      coursesIndex: coursesIndex,
      coursesList: coursesList,
    }, () => {
      console.log("done", this.state.coursesIndex, this.state.coursesList);
    })
  }

  getUsers(page = 1) {
    const offset = (page-1) * this.state.perPage;
    const requestUrl = this.constructApiUrl(apiConfig.learnersDetailed, this.state.searchQuery, this.state.ordering, this.state.perPage, offset);
    trackPromise(
      fetch((requestUrl), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          learnersList: json['results'],
          count: json['count'],
          pages: Math.ceil(json['count'] / this.state.perPage),
          currentPage: page,
        })
      )
    )
  }

  setPerPage(newValue) {
    this.setState({
      perPage: newValue,
    }, () => {
      this.getUsers();
    })
  }

  setSearchQuery(newValue) {
    this.setState({
      searchQuery: newValue
    }, () => {
      this.getUsers();
    })
  }

  setOrdering(newValue) {
    this.setState({
      ordering: newValue
    }, () => {
      this.getUsers();
    })
  }

  componentDidMount() {
    this.getCourses();
    this.getUsers();
  }

  render() {

    const coursesFilter = this.state.selectedCourses.length ? this.state.selectedCourses : this.state.coursesList;

    const headerCourseColumns = coursesFilter.map((course, index) => {
      return(
        <div className={styles['course-info-column']}>
          {this.state.coursesIndex[course]['name']}
        </div>
      )
    })

    const floatingListItems = this.state.learnersList.map((user, index) => {
      return (
        <li key={`floating+${user['id']}`} className={styles['user-list-item']}>
          <div className={styles['user-fullname']}>
            <Link
              className={styles['user-fullname-link']}
              to={'/figures/user/' + user['id']}
            >
              {user['name']}
            </Link>
          </div>
        </li>
      )
    });

    const scrollingListItems = this.state.learnersList.map((user, index) => {

      const userCoursesImmutable = Immutable.fromJS(user['courses']);
      const userCoursesRender = coursesFilter.map((course, i) => {
        console.log("course filter", course);
        const userProgress = userCoursesImmutable.find(singleCourse => singleCourse.get('course_id') === course);
        return (
          <div className={styles['single-course-progress']}>
            {userProgress ? [
              <div className={styles['data-group']}>
                <span className={styles['data-label']}>Sections</span>
                <span className={styles['data']}>{userProgress.getIn(['progress_data', 'course_progress_details', 'sections_worked'])}/{userProgress.getIn(['progress_data', 'course_progress_details', 'sections_possible'])}</span>
              </div>,
              <div className={styles['data-group']}>
                <span className={styles['data-label']}>Points</span>
                <span className={styles['data']}>{userProgress.getIn(['progress_data', 'course_progress_details', 'points_earned'])}/{userProgress.getIn(['progress_data', 'course_progress_details', 'points_possible'])}</span>
              </div>,
              <div className={styles['data-group']}>
                <span className={styles['data-label']}>Progress</span>
                <span className={styles['data']}>{userProgress.getIn(['progress_data', 'course_progress'])*100}%</span>
              </div>
            ] : (
              <span className={styles['no-data']}>-</span>
            )}
          </div>
        )
      })

      return (
        <li key={`scrolling+${user['id']}`} className={styles['user-list-item']}>
          <div className={styles['username']}>
            {user['username']}
          </div>
          <div className={styles['email']}>
            {user['email']}
          </div>
          {userCoursesRender}
        </li>
      )
    })

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentStatic
            title='Learners progress overview'
            subtitle={'This view allows you to view a snapshot of your sites learners progress. Total number of results: ' + this.state.count + '.'}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container-max': true, 'users-content': true})}>
          <ListSearch
            valueChangeFunction={this.setSearchQuery}
            inputPlaceholder='Search by users name, username or email...'
          />
          {this.state.pages ? (
            <Paginator
              pageSwitchFunction={this.getUsers}
              currentPage={this.state.currentPage}
              perPage={this.state.perPage}
              pages={this.state.pages}
              changePerPageFunction={this.setPerPage}
            />
          ) : ''}
          <div className={styles['users-overview-list']}>
            <ul className={styles['list-floating-columns']}>
              <li key='list-header' className={cx(styles['user-list-item'], styles['list-header'])}>
                <div className={styles['user-fullname']}>
                  <button
                    className={styles['sorting-header-button']}
                    onClick={() => (this.state.ordering !== 'profile__name') ? this.setOrdering('profile__name') : this.setOrdering('-profile__name')}
                  >
                    <span>
                      User full name
                    </span>
                    {(this.state.ordering === 'profile__name') ? (
                      <FontAwesomeIcon icon={faAngleDoubleUp} />
                    ) : (this.state.ordering === '-profile__name') ? (
                      <FontAwesomeIcon icon={faAngleDoubleDown} />
                    ) : ''}
                  </button>
                </div>
              </li>
              {floatingListItems}
            </ul>
            <ul className={styles['list-scrolling-columns']}>
              <li key='list-header' className={cx(styles['user-list-item'], styles['list-header'])}>
                <div className={styles['username']}>
                  <button
                    className={styles['sorting-header-button']}
                    onClick={() => (this.state.ordering !== 'username') ? this.setOrdering('username') : this.setOrdering('-username')}
                  >
                    <span>
                      Username
                    </span>
                    {(this.state.ordering === 'username') ? (
                      <FontAwesomeIcon icon={faAngleDoubleUp} />
                    ) : (this.state.ordering === '-username') ? (
                      <FontAwesomeIcon icon={faAngleDoubleDown} />
                    ) : ''}
                  </button>
                </div>
                <div className={styles['email']}>
                  <button
                    className={styles['sorting-header-button']}
                    onClick={() => (this.state.ordering !== 'email') ? this.setOrdering('email') : this.setOrdering('-email')}
                  >
                    <span>
                      Email
                    </span>
                    {(this.state.ordering === 'username') ? (
                      <FontAwesomeIcon icon={faAngleDoubleUp} />
                    ) : (this.state.ordering === '-username') ? (
                      <FontAwesomeIcon icon={faAngleDoubleDown} />
                    ) : ''}
                  </button>
                </div>
                {headerCourseColumns}
              </li>
              {scrollingListItems}
            </ul>
          </div>
          {this.state.pages ? (
            <Paginator
              pageSwitchFunction={this.getUsers}
              currentPage={this.state.currentPage}
              perPage={this.state.perPage}
              pages={this.state.pages}
              changePerPageFunction={this.setPerPage}
            />
          ) : ''}
        </div>
      </div>
    );
  }
}

export default ProgressOverview
