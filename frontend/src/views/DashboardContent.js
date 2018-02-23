import React, { Component } from 'react';
import classNames from 'classnames/bind';
import styles from './_dashboard-content.scss';
import BaseStatCard from 'base/components/stat-cards/BaseStatCard';
import CoursesList from 'base/components/courses-list/CoursesList';

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


class DashboardContent extends Component {
  constructor(props) {
    super(props);

    this.state = {

    };

    this.apiSimulator = this.apiSimulator.bind(this);
  }

  apiSimulator = (dataParameter, dataAmount) => {
    console.log('API poziv');
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
          cardTitle='Card 1'
          getDataFunction={this.apiSimulator}
          dataParameter='number-of-learners'
        />
        <BaseStatCard
          cardTitle='Card 2'
          getDataFunction={this.apiSimulator}
          dataParameter='average-progress'
          dataType='percentage'
        />
        <BaseStatCard
          cardTitle='Card 3'
          getDataFunction={this.apiSimulator}
          dataParameter='number-of-learners'
          singleValue
          value='41d 36h 22m'
        />
        <BaseStatCard
          cardTitle='Card 4'
          getDataFunction={this.apiSimulator}
          dataParameter='average-progress'
          dataType='percentage'
        />
        <CoursesList
          getIdListFunction={this.courseIdListApiSimulator}
          getCourseDataFunction={this.courseDataApiSimulator}
        />
      </div>
    );
  }
}

export default DashboardContent;
