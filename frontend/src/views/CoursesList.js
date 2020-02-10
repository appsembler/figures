import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import apiConfig from 'base/apiConfig';
import { trackPromise } from 'react-promise-tracker';
import styles from './_courses-list-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentStatic from 'base/components/header-views/header-content-static/HeaderContentStatic';
import Paginator from 'base/components/layout/Paginator';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck } from '@fortawesome/free-solid-svg-icons';

import classNames from 'classnames/bind';
let cx = classNames.bind(styles);

const parseCourseDate = (fetchedDate) => {
  if (fetchedDate === null) {
    return "-";
  } else if (Date.parse(fetchedDate)) {
    const tempDate = new Date(fetchedDate);
    return tempDate.toUTCString();
  } else {
    return fetchedDate;
  }
}


class CoursesList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      coursesList: [],
      perPage: 20,
      count: 0,
      pages: 0,
      currentPage: 1,
    };

    this.getCourses = this.getCourses.bind(this);
    this.setPerPage = this.setPerPage.bind(this);
  }

  getCourses(page = 1) {
    const offset = (page-1) * this.state.perPage;
    const requestUrl = apiConfig.coursesGeneral + '?limit=' + this.state.perPage + '&offset=' + offset;
    trackPromise(
      fetch((requestUrl), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          coursesList: json['results'],
          count: json['count'],
          pages: Math.ceil(json['count'] / this.state.perPage),
          currentPage: page,
        })
      )
    )
  }

  setCurrentPage(newValue) {
    this.setState({
      currentPage: newValue,
    })
  }

  setPerPage(newValue) {
    this.setState({
      perPage: newValue
    }, () => {
      this.getCourses();
    })
  }

  componentDidMount() {
    this.getCourses();
  }

  render() {

    const listItems = this.state.coursesList.map((course, index) => {
      return (
        <li key={course['id']} className={styles['course-list-item']}>
          <div className={styles['course-name']}>
            <Link
              className={styles['course-name-link']}
              to={'/figures/course/' + course['course_id']}
            >
              {course['course_name']}
            </Link>
          </div>
          <div className={styles['course-id']}>
            {course['course_id']}
          </div>
          <div className={styles['start-date']}>
            {parseCourseDate(course['start_date'])}
          </div>
          <div className={styles['self-paced']}>
            {course['self_paced'] ? <FontAwesomeIcon icon={faCheck} className={styles['checkmark-icon']} /> : '-'}
          </div>
          <div className={styles['enrolments']}>
            {course['metrics']['enrollment_count']}
          </div>
          <div className={styles['completions']}>
            {course['metrics']['num_learners_completed']}
          </div>
          <div className={styles['action-container']}>
            <Link
              className={styles['course-action']}
              to={'/figures/course/' + course['course_id']}
            >
              Details
            </Link>
          </div>
        </li>
      )
    })

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentStatic
            title='Courses list'
            subtitle={'This view allows you to browse your sites courses. Total number of courses: ' + this.state.count + '.'}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'courses-content': true})}>
          {this.state.pages ? (
            <Paginator
              pageSwitchFunction={this.getCourses}
              currentPage={this.state.currentPage}
              perPage={this.state.perPage}
              pages={this.state.pages}
              changePerPageFunction={this.setPerPage}
            />
          ) : ''}
          <ul className={styles['courses-list']}>
            <li key='list-header' className={cx(styles['course-list-item'], styles['list-header'])}>
              <div className={styles['course-name']}>
                Course name:
              </div>
              <div className={styles['course-id']}>
                Course ID:
              </div>
              <div className={styles['start-date']}>
                Course start:
              </div>
              <div className={styles['self-paced']}>
                Self paced:
              </div>
              <div className={styles['enrolments']}>
                Enrolments:
              </div>
              <div className={styles['completions']}>
                Completions:
              </div>
              <div className={styles['action-container']}>

              </div>
            </li>
            {listItems}
          </ul>
          {this.state.pages ? (
            <Paginator
              pageSwitchFunction={this.getCourses}
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

export default CoursesList
