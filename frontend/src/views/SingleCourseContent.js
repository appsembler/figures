import React, { Component } from 'react';
import classNames from 'classnames/bind';
import styles from './_single-course-content.scss';
import BaseStatCard from 'base/components/stat-cards/BaseStatCard';
import LearnerStatistics from 'base/components/learner-statistics/LearnerStatistics';
import CourseLearnersList from 'base/components/course-learners-list/CourseLearnersList';

let cx = classNames.bind(styles);

const testNumberOfLearners = [
  {
    value: 6,
    period: '11/2017'
  },
  {
    value: 4,
    period: '12/2017'
  },
  {
    value: 12,
    period: '01/2017'
  },
  {
    value: 51,
    period: '02/2017'
  },
  {
    value: 31,
    period: '03/2017'
  },
  {
    value: 132,
    period: '04/2017'
  },
]

const testAverageProgress = [
  {
    value: 0.3,
    period: '11/2017'
  },
  {
    value: 0.4,
    period: '12/2017'
  },
  {
    value: 0.6,
    period: '01/2017'
  },
  {
    value: 0.9,
    period: '02/2017'
  },
  {
    value: 0.71,
    period: '03/2017'
  },
  {
    value: 0.46,
    period: '04/2017'
  },
]

const testCourseIds = [
  'A193-2016Q4',
  'A194-2016Q4',
  'A195-2016Q4',
]

const testCourseData = {
  'A193-2016Q4': {
    courseTitle: 'This is the course title',
    isSelfPaced: false,
    startDate: '30-12-2018',
    endDate: '30-12-2018',
    courseStaff: ['Matej Grozdanović', 'Harry Klein', 'Nate Aune'],
    learnersEnrolled: 150,
    averageProgress: 0.41,
    averageCompletionTime: '41 days',
    numberLearnersCompleted: 38,
  },
  'A194-2016Q4': {
    courseTitle: 'Another course title',
    isSelfPaced: false,
    startDate: '30-12-2018',
    endDate: '30-12-2018',
    courseStaff: ['Harry Klein', 'Nate Aune'],
    learnersEnrolled: 350,
    averageProgress: 0.21,
    averageCompletionTime: '31 days',
    numberLearnersCompleted: 57,
  },
  'A195-2016Q4': {
    courseTitle: 'Introduction to fake courses and fake certification',
    isSelfPaced: true,
    startDate: '',
    endDate: '',
    courseStaff: ['Matej Grozdanović', 'Nate Aune'],
    learnersEnrolled: 110,
    averageProgress: 0.81,
    averageCompletionTime: '65 days',
    numberLearnersCompleted: 38,
  }
}


class SingleCourseContent extends Component {
  constructor(props) {
    super(props);

    this.state = {

    };

    this.apiSimulator = this.apiSimulator.bind(this);
  }

  apiSimulator = (dataParameter, dataAmount) => {
    let sourceData;
    if (dataParameter === 'number-of-learners') {
      sourceData = testNumberOfLearners;
    } else if (dataParameter === 'average-progress') {
      sourceData = testAverageProgress;
    }
    if (dataAmount > sourceData.length) {
      return sourceData;
    } else {
      return sourceData.slice(-dataAmount);
    }
  };

  courseIdListApiSimulator = () => {
    return testCourseIds;
  }

  courseDataApiSimulator = (courseId) => {
    return testCourseData[courseId];
  }

  render() {
    return (
      <div className={cx({ 'container': true, 'base-grid-layout': true, 'dashboard-content': true})}>
        <BaseStatCard
          cardTitle='Number of enrolled learners'
          cardDescription='Leverage agile frameworks to provide a robust synopsis for high level overviews. Iterative approaches to corporate strategy foster collaborative thinking to further the overall value proposition.'
          getDataFunction={this.apiSimulator}
          dataParameter='number-of-learners'
        />
        <BaseStatCard
          cardTitle='Average course progress'
          cardDescription='At the end of the day, going forward, a new normal that has evolved from generation X is on the runway heading towards a streamlined cloud solution.'
          getDataFunction={this.apiSimulator}
          dataParameter='average-progress'
          dataType='percentage'
        />
        <BaseStatCard
          cardTitle='Average time to complete'
          cardDescription='Organically grow the holistic world view of disruptive innovation via workplace diversity and empowerment.'
          getDataFunction={this.apiSimulator}
          dataParameter='number-of-learners'
          singleValue
          value='41d 36h 22m'
        />
        <BaseStatCard
          cardTitle='User course completions'
          cardDescription='Organically grow the holistic world view of disruptive innovation via workplace diversity and empowerment. Bring to the table win-win survival strategies to ensure proactive domination.'
          getDataFunction={this.apiSimulator}
          dataParameter='average-progress'
          dataType='percentage'
        />
        <LearnerStatistics />
        <CourseLearnersList />
      </div>
    );
  }
}

export default SingleCourseContent;
