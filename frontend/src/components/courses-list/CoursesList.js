import React, { Component } from 'react';
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
      coursesData: [],
    };

    this.changeSorting = this.changeSorting.bind(this);
    this.sortByParameter = this.sortByParameter.bind(this);
    this.populateCourseData = this.populateCourseData.bind(this);
  }

  changeSorting = (parameter) => {
    let dataParameter;
    if (parameter === 'alphabetically') {
      dataParameter = 'courseTitle';
    } else if (parameter === 'learners-enrolled') {
      dataParameter = 'learnersEnrolled';
    } else if (parameter === 'average-progress') {
      dataParameter = 'averageProgress';
    } else if (parameter === 'completion-time') {
      dataParameter = 'averageCompletionTime';
    } else if (parameter === 'completed-learners') {
      dataParameter = 'numberLearnersCompleted';
    }
    let sortedData = this.sortByParameter(this.state.coursesData, dataParameter);
    this.setState({
      coursesData: sortedData,
      sortListBy: parameter,
    })
  }

  sortByParameter = (data, parameter) => {
    data.sort(function(a, b) {
      if(a[parameter] < b[parameter]) return -1;
      if(a[parameter] > b[parameter]) return 1;
      return 0;
    });
    return data;
  }

  populateCourseData = () => {
    let coursesData = [];
    let tempItem = {};
    let courseIds = this.props.getIdListFunction();
    courseIds.forEach((id, index) => {
      tempItem = this.props.getCourseDataFunction(id);
      tempItem.courseId = id;
      coursesData.push(tempItem);
    });
    this.setState({
      coursesData: coursesData,
    });
  }

  componentDidMount() {
    this.populateCourseData();
  }

  render() {
    const courseItems = this.state.coursesData.map((item, index) => {
      return (
        <CoursesListItem
          courseName={item.courseTitle}
          courseId={item.courseId}
          courseIsSelfPaced={item.isSelfPaced}
          startDate={item.startDate}
          endDate={item.endDate}
          courseStaff={item.courseStaff}
          averageCompletionTime={item.averageCompletionTime}
          averageProgress={item.averageProgress}
          learnersEnrolled={item.learnersEnrolled}
          numberLearnersCompleted={item.numberLearnersCompleted}
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
  listTitle: 'Course data:'
}

CoursesList.propTypes = {
  listTitle: PropTypes.string,
  getIdListFunction: PropTypes.func,
  getCourseDataFunction: PropTypes.func,
};

export default CoursesList;
