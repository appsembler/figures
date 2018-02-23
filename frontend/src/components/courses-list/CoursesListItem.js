import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import styles from './_courses-list-item.scss';


class CoursesListItem extends Component {

  render() {
    const courseStaff = this.props.courseStaff.map((item, index) => {
      return (
        <span className={styles['value']}>{item}</span>
      )
    });

    return (
      <div className={styles['course-list-item']} key={this.props.courseId}>
        <div className={styles['general-info-section']}>
          <span className={styles['course-id']}>{this.props.courseId}</span>
          <span className={styles['course-name']}>{this.props.courseName}</span>
          {this.props.courseIsSelfPaced ? (
            <div className={styles['label-value']}>
              <span className={styles['label']}>Course dates:</span>
              <span className={styles['value']}>This course is self-paced</span>
            </div>
          ) : [
            <div className={styles['label-value']}>
              <span className={styles['label']}>Start date:</span>
              <span className={styles['value']}>{this.props.startDate}</span>
            </div>,
            <div className={styles['label-value']}>
              <span className={styles['label']}>End date:</span>
              <span className={styles['value']}>{this.props.endDate}</span>
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
                {this.props.averageProgress*100}%
              </span>
            </div>
            <div className={styles['single-stat']}>
              <span className={styles['stat-label']}>
                Average time to completion:
              </span>
              <span className={styles['stat-value']}>
                {this.props.averageCompletionTime}
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
          <Link to="#" className={styles['course-button']}>Course details</Link>
        </div>
      </div>
    )
  }
}

CoursesListItem.defaultProps = {

}

CoursesListItem.propTypes = {

};

export default CoursesListItem;
