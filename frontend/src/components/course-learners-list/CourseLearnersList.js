import React, { Component } from 'react';
import PropTypes from 'prop-types';
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
      allDataDisplayed: false,
    };
    this.retrieveData = this.retrieveData.bind(this);
  }

  retrieveData = (amountToFetch) => {
    const testData = [
      {
        name: 'Hans Gruber',
        country: 'Germany',
        dateEnrolled: '10-23-2017',
        courseProgress: '59%',
        courseCompleted: false,
        dateCompleted: '',
      },
      {
        name: 'John McClane',
        country: 'USA',
        dateEnrolled: '08-13-2016',
        courseProgress: '100%',
        courseCompleted: true,
        dateCompleted: '12-04-2017',
      },
      {
        name: 'John McClane',
        country: 'USA',
        dateEnrolled: '08-13-2016',
        courseProgress: '100%',
        courseCompleted: true,
        dateCompleted: '12-04-2017',
      },
    ]
    let temp = this.state.displayedData;
    this.setState({
      displayedData: temp.concat(testData.slice(temp.length, (temp.length + amountToFetch))),
      allDataDisplayed: (amountToFetch >= testData.slice(temp.length).length),
    })
  }

  componentDidMount() {
    this.retrieveData(this.props.paginationMaxRows);
  }


  render() {
    const learnersRender = this.state.displayedData.length ? this.state.displayedData.map((learner, index) => {
      return (
        <li key={index} className={styles['learner-row']}>
          <span className={styles['name']}>{learner.name}</span>
          <span className={styles['country']}>{learner.country}</span>
          <span className={styles['date-enrolled']}>{learner.dateEnrolled}</span>
          <span className={styles['course-progress']}>{learner.courseProgress}</span>
          <span className={styles['course-completed']}>{learner.courseCompleted && <FontAwesomeIcon icon={faCheck} className={styles['completed-icon']} />}</span>
          <span className={styles['date-completed']}>{learner.courseCompleted ? learner.dateCompleted : '-'}</span>
        </li>
      );
    }) : '';

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
          {!this.state.allDataDisplayed && <button className={styles['load-more-button']} onClick={() => this.retrieveData(this.props.paginationMaxRows)}>Load more</button>}
        </div>
      </section>
    )
  }
}

CourseLearnersList.defaultProps = {
  listTitle: 'Per learner info:',
  paginationMaxRows: 2,
}

CourseLearnersList.propTypes = {
  listTitle: PropTypes.string,
  paginationMaxRows: PropTypes.number,
};

export default CourseLearnersList;
