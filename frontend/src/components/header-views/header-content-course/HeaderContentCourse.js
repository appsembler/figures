import React, { Component } from 'react';
import classNames from 'classnames/bind';
import styles from './_header-content-course.scss';
import { ResponsiveContainer, BarChart, Bar, XAxis, Tooltip } from 'recharts';

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

class CustomTooltip extends Component {

  render() {
    const { active } = this.props;

    if (active) {
      const { payload } = this.props;
      return (
        <div className={styles['bar-tooltip']}>
          <span className={styles['tooltip-value']}>{payload[0].value}</span>
          <p>learners currently at this section</p>
        </div>
      );
    }

    return null;
  }
}

class HeaderContentCourse extends Component {

  render() {

    const displayCourseHeaderGraph = false;

    return (
      <section className={styles['header-content-course']}>
        <div className={cx({ 'main-content': true, 'container': true})}>
          <div className={styles['course-title']}>
            {this.props.courseName}
          </div>
          <div className={styles['course-info']}>
            <span className={styles['course-code']}>{this.props.courseCode}</span>
            <span className={styles['course-info-separator']}>|</span>
            {this.props.isSelfPaced ? (
              <span className={styles['course-date']}>This course is self-paced</span>
            ) : [
              <span key='courseStart' className={styles['course-date']}>Starts: {parseCourseDate(this.props.startDate)}</span>,
              this.props.endDate && <span key='separator' className={styles['course-info-separator']}>|</span>,
              this.props.endDate && <span key='courseEnd' className={styles['course-date']}>Ends: {parseCourseDate(this.props.endDate)}</span>,
            ]}
          </div>
          {displayCourseHeaderGraph ? [
            <span className={styles['text-separator']} />,
            <div className={styles['learners-info']}>
              <strong>{this.props.learnersEnrolled && this.props.learnersEnrolled['current_month']}</strong> learners currently enrolled, progressing through sections as displayed below:
            </div>
          ] : (
            <span className={styles['graph-bottom-padding']} />
          )}
        </div>
        {displayCourseHeaderGraph ? [
          <div className={cx({ 'graph-bars-container': true, 'container': true})}>
            <ResponsiveContainer width="100%" height={140}>
              <BarChart
                data={this.props.data}
                margin={{top: 0, bottom: 0, left: 0, right: 0}}
                barCategoryGap={4}
              >
                <Tooltip
                  content={<CustomTooltip/>}
                  cursor={{ fill: 'rgba(255, 255, 255, 0.15)'}}
                  offset={0}
                />
                <Bar dataKey='value' stroke='none' fill='#ffffff' fillOpacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          </div>,
          <div className={styles['graph-labels-wrapper']}>
            <div className={cx({ 'graph-labels-container': true, 'container': true})}>
              <ResponsiveContainer width="100%" height={100}>
                <BarChart
                  data={this.props.data}
                  margin={{top: 0, bottom: 0, left: 0, right: 0}}
                  barCategoryGap={4}
                >
                  <XAxis
                    dataKey='lessonTitle'
                    axisLine={false}
                    tickLine={false}
                    height={100}
                    angle={90}
                    textAnchor="start"
                    interval={0}
                    //tick={<CustomXAxisLabel />}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ] : ""}
      </section>
    );
  }
}

HeaderContentCourse.defaultProps = {
  data: [
    {
      lessonTitle: 'Lesson 1',
      lessonSubtitle: 'Something something something',
      value: 12
    },
    {
      lessonTitle: 'Lesson 2',
      lessonSubtitle: 'Something something something something',
      value: 19
    },
    {
      lessonTitle: 'Lesson 3',
      lessonSubtitle: 'Something something',
      value: 38
    },
    {
      lessonTitle: 'Lesson 4',
      lessonSubtitle: 'Something something something',
      value: 31
    },
    {
      lessonTitle: 'Lesson 5',
      lessonSubtitle: 'Something something something',
      value: 59
    },
    {
      lessonTitle: 'Lesson 6',
      lessonSubtitle: 'Something something something',
      value: 12
    },
    {
      lessonTitle: 'Lesson 7',
      lessonSubtitle: 'Something',
      value: 14
    },
    {
      lessonTitle: 'Lesson 8',
      lessonSubtitle: 'Something something something',
      value: 7
    },
    {
      lessonTitle: 'Lesson 9',
      lessonSubtitle: 'Something something something',
      value: 9
    },
    {
      lessonTitle: 'Lesson 10',
      lessonSubtitle: 'Something something something',
      value: 16
    },
    {
      lessonTitle: 'Lesson 11',
      lessonSubtitle: 'Something something something',
      value: 22
    },
    {
      lessonTitle: 'Lesson 12',
      lessonSubtitle: 'Something something something',
      value: 12
    },
    {
      lessonTitle: 'Lesson 13',
      lessonSubtitle: 'Something something something',
      value: 3
    },
    {
      lessonTitle: 'Lesson 14',
      lessonSubtitle: 'Something something something',
      value: 14
    },
    {
      lessonTitle: 'Lesson 15',
      lessonSubtitle: 'Something something something',
      value: 30
    },
    {
      lessonTitle: 'Lesson 16',
      lessonSubtitle: 'Something something something',
      value: 14
    }
  ]
}

export default HeaderContentCourse;
