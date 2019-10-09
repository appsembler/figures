import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import styles from './_user-courses-list.scss';
import classNames from 'classnames/bind';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck } from '@fortawesome/free-solid-svg-icons';

let cx = classNames.bind(styles);

class UserCoursesList extends Component {

  render() {

    const coursesRender = this.props.enrolledCoursesData.map((course, index) => {
      const progressBarWidth = (course.getIn(['progress_data', 'course_progress'], 0)*100).toFixed(0) + '%';

      return (
        <div key={index} className={cx({'stat-card': true, 'course-item': true})}>
          <div className={styles['course-info']}>
            <span className={styles['course-code']}>{course['course_code']}</span>
            <Link className={styles['course-name']} to={"/figures/course/" + course.getIn(['course_id'], "")}>{course.getIn(['course_name'], "")}</Link>
          </div>
          <ul className={styles['user-stats']}>
            <li className={styles['stat']}>
              <span className={styles['stat-label']}>
                Date enrolled:
              </span>
              <span className={styles['stat-value']}>
                {course.getIn(['date_enrolled'])}
              </span>
            </li>
            <li className={styles['stat']}>
              <span className={styles['stat-label']}>
                Course completed:
              </span>
              <span className={styles['stat-value']}>
                {course.getIn(['progress_data', 'course_completed']) ? <FontAwesomeIcon icon={faCheck} className={styles['completed-icon']} /> : '-'}
              </span>
            </li>
            <li className={styles['stat']}>
              <span className={styles['stat-label']}>
                Points earned:
              </span>
              <span className={styles['stat-value']}>
                {course.getIn(['progress_data', 'course_progress_details', 'points_earned'], 0)} (of {course.getIn(['progress_data', 'course_progress_details', 'points_possible'], 0)})
              </span>
            </li>
            <li className={styles['stat']}>
              <span className={styles['stat-label']}>
                Overall progress:
              </span>
              <span className={styles['stat-value']}>
                {(course.getIn(['progress_data', 'course_progress'], 0)*100).toFixed(2)}%
              </span>
            </li>
          </ul>
          <div className={styles['progress-bar']}>
            <span className={cx({'bar': true, 'finished': course.getIn(['progress_data', 'course_completed'])})} style={{width: progressBarWidth}}></span>
          </div>
        </div>
      )
    })

    return (
      <section className={styles['user-courses-list']}>
        {coursesRender}
      </section>
    )
  }
}

export default UserCoursesList;
