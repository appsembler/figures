import React, { Component } from 'react';
import { List } from 'immutable';
import PropTypes from 'prop-types';
import styles from './_courses-list.scss';
import classNames from 'classnames/bind';
import CoursesListItem from './CoursesListItem';

let cx = classNames.bind(styles);

class CoursesList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      sortListBy: '',
      coursesList: List()
    };

    this.changeSorting = this.changeSorting.bind(this);
  }

  changeSorting = (parameter) => {
    let coursesList = this.state.coursesList;
    if (parameter === 'alphabetically') {
      coursesList = coursesList.sortBy(item => item.getIn(['course_name']))
    } else if (parameter === 'learners-enrolled') {
      coursesList = coursesList.sortBy(item => item.getIn(['learners_enrolled', 'current_month'])).reverse()
    } else if (parameter === 'average-progress') {
      coursesList = coursesList.sortBy(item => item.getIn(['average_progress', 'current_month'])).reverse()
    } else if (parameter === 'completion-time') {
      coursesList = coursesList.sortBy(item => item.getIn(['average_days_to_complete', 'current_month'])).reverse()
    } else if (parameter === 'completed-learners') {
      coursesList = coursesList.sortBy(item => item.getIn(['users_completed', 'current_month'])).reverse()
    }
    this.setState({
      coursesList: coursesList,
      sortListBy: parameter,
    })
  }

  componentWillReceiveProps = (nextProps) => {
    if (nextProps !== this.props) {
      this.setState({
        coursesList: List(nextProps.coursesList)
      })
    }
  }

  render() {
    const courseItems = this.state.coursesList.map((item, index) => {
      return (
        <CoursesListItem
          courseName={item.get('course_name')}
          courseId={item.get('course_id')}
          courseCode={item.get('course_code')}
          courseIsSelfPaced={item.get('self_paced')}
          startDate={item.get('start_date')}
          endDate={item.get('end_date')}
          courseStaff={item.get('staff')}
          averageCompletionTime={item.getIn(['average_days_to_complete', 'current_month'])}
          averageProgress={item.getIn(['average_progress', 'current_month'])}
          learnersEnrolled={item.getIn(['learners_enrolled', 'current_month'])}
          numberLearnersCompleted={item.getIn(['users_completed', 'current_month'])}
          key={index}
        />
      )
    })

    return (
      <section className={styles['courses-list']}>
        <div className={styles['header']}>
          <div className={styles['header-title']}>
            {this.props.listTitle}
          </div>
          <div className={styles['sort-container']}>
            <span>Sort by:</span>
            <ul>
              <li onClick={this.changeSorting.bind(this, 'alphabetically')} className={cx({ 'sort-item': true, 'active': (this.state.sortListBy === 'alphabetically')})}>A-Z</li>
              <li onClick={this.changeSorting.bind(this, 'learners-enrolled')} className={cx({ 'sort-item': true, 'active': (this.state.sortListBy === 'learners-enrolled')})}>Learners enrolled</li>
              <li onClick={this.changeSorting.bind(this, 'average-progress')} className={cx({ 'sort-item': true, 'active': (this.state.sortListBy === 'average-progress')})}>Average progress</li>
              <li onClick={this.changeSorting.bind(this, 'completion-time')} className={cx({ 'sort-item': true, 'active': (this.state.sortListBy === 'completion-time')})}>Avg. time for completion</li>
              <li onClick={this.changeSorting.bind(this, 'completed-learners')} className={cx({ 'sort-item': true, 'active': (this.state.sortListBy === 'completed-learners')})}>No. of compl. learners</li>
            </ul>
          </div>
        </div>
        <div className={styles['items-container']}>
          {courseItems}
        </div>
      </section>
    )
  }
}

CoursesList.defaultProps = {
  listTitle: 'Course data:',
  CoursesList: []
}

CoursesList.propTypes = {
  listTitle: PropTypes.string,
  coursesList: PropTypes.array
};

export default CoursesList;
