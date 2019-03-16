import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import styles from './_courses-list-item.scss';

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

class CoursesListItem extends Component {

  render() {
    const courseStaff = this.props.courseStaff.map((item, index) => {
      return (
        <span key={index} className={styles['value']}>{item.get('fullname')}</span>
      )
    });

    return (
      <Link to={'/figures/course/' + this.props.courseId} className={styles['course-list-item']} key={this.props.courseId}>
        <div className={styles['general-info-section']}>
          <span className={styles['course-id']}>{this.props.courseCode}</span>
          <span className={styles['course-name']}>{this.props.courseName}</span>
          {this.props.courseIsSelfPaced ? (
            <div className={styles['label-value']}>
              <span className={styles['label']}>Course dates:</span>
              <span className={styles['value']}>This course is self-paced</span>
            </div>
          ) : [
            <div key='startDate' className={styles['label-value']}>
              <span className={styles['label']}>Start date:</span>
              <span className={styles['value']}>{parseCourseDate(this.props.startDate)}</span>
            </div>,
            <div key='endDate' className={styles['label-value']}>
              <span className={styles['label']}>End date:</span>
              <span className={styles['value']}>{parseCourseDate(this.props.startDate)}</span>
            </div>
          ]}
          <div className={styles['label-value']}>
            <span className={styles['label']}>Course staff:</span>
            {courseStaff}
          </div>
        </div>
        <span className={styles['sections-separator']} />
        <div className={styles['stats-section']}>
          <div className={styles['stats-section-inner']}>
            <div className={styles['single-stat']}>
              <span className={styles['stat-label']}>
                Learners enrolled:
              </span>
              <span className={styles['stat-value']}>
                {this.props.learnersEnrolled}
              </span>
            </div>
            <div className={styles['single-stat']}>
              <span className={styles['stat-label']}>
                Average progress:
              </span>
              <span className={styles['stat-value']}>
                {(this.props.averageProgress*100).toFixed(2)}%
              </span>
            </div>
            <div className={styles['single-stat']}>
              <span className={styles['stat-label']}>
                Average days to complete:
              </span>
              <span className={styles['stat-value']}>
                {this.props.averageCompletionTime ? this.props.averageCompletionTime : 'n/a'}
              </span>
            </div>
            <div className={styles['single-stat']}>
              <span className={styles['stat-label']}>
                No. of learners to complete:
              </span>
              <span className={styles['stat-value']}>
                {this.props.numberLearnersCompleted}
              </span>
            </div>
          </div>
        </div>
        <span className={styles['sections-separator']} />
        <div className={styles['button-section']}>
          <Link to={'/figures/course/' + this.props.courseId} className={styles['course-button']}>Course details</Link>
        </div>
      </Link>
    )
  }
}

CoursesListItem.defaultProps = {

}

CoursesListItem.propTypes = {
  courseStaff: PropTypes.array,
  courseId: PropTypes.string,
  courseName: PropTypes.string,
  courseIsSelfPaced: PropTypes.bool,
  startDate: PropTypes.string,
  endDate: PropTypes.string,
  learnersEnrolled: PropTypes.number,
  averageProgress: PropTypes.number,
  averageCompletionTime: PropTypes.number,
  numberLearnersCompleted: PropTypes.number,
};

export default CoursesListItem;
