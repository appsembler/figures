import React, { Component } from 'react';
import Immutable from 'immutable';
import { Link } from 'react-router-dom';
import Select from 'react-select';
import styles from './_csv-reports-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentCsvReports from 'base/components/header-views/header-content-csv-reports/HeaderContentCsvReports';

import classNames from 'classnames/bind';
let cx = classNames.bind(styles);

const parseReportDate = (fetchedDate) => {
  if (fetchedDate === null) {
    return "-";
  } else if (Date.parse(fetchedDate)) {
    const tempDate = new Date(fetchedDate);
    return tempDate.toUTCString();
  } else {
    return fetchedDate;
  }
}

// month naming
const monthNames = {
  1: 'January',
  2: 'February',
  3: 'March',
  4: 'April',
  5: 'May',
  6: 'June',
  7: 'July',
  8: 'August',
  9: 'September',
  10: 'October',
  11: 'November',
  12: 'December',
}

//some dummy data for testing before we hook up real APIs
const UserReports = [
  {
    report_name: 'User Report',
    generated_at: '2018-01-23T01:23:45.123456Z',
    report_url: '#',
    report_type: 'User Report'
  },
  {
    report_name: 'User Report',
    generated_at: '2018-02-22T01:23:45.123456Z',
    report_url: '#',
    report_type: 'User Report'
  },
  {
    report_name: 'User Report',
    generated_at: '2018-02-21T01:23:45.123456Z',
    report_url: '#',
    report_type: 'User Report'
  },
  {
    report_name: 'User Report',
    generated_at: '2019-02-22T01:23:45.123456Z',
    report_url: '#',
    report_type: 'User Report'
  },
  {
    report_name: 'User Report',
    generated_at: '2019-02-21T01:23:45.123456Z',
    report_url: '#',
    report_type: 'User Report'
  }
]

const GradeReports = [
  {
    report_name: 'Grade Report',
    generated_at: '2018-01-23T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Grade Report'
  },
  {
    report_name: 'Grade Report',
    generated_at: '2018-02-22T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Grade Report'
  },
  {
    report_name: 'Users Report',
    generated_at: '2018-02-21T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Grade Report'
  },
  {
    report_name: 'Grade Report',
    generated_at: '2019-02-22T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Grade Report'
  },
  {
    report_name: 'Users Report',
    generated_at: '2019-02-21T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Grade Report'
  }
]

const CourseMetricsReports = [
  {
    report_name: 'Course Metrics Report',
    generated_at: '2018-01-23T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Course Metrics Report'
  },
  {
    report_name: 'Course Metrics Report',
    generated_at: '2018-02-22T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Course Metrics Report'
  },
  {
    report_name: 'Course Metrics Report',
    generated_at: '2018-02-21T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Course Metrics Report'
  },
  {
    report_name: 'Course Metrics Report',
    generated_at: '2019-02-22T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Course Metrics Report'
  },
  {
    report_name: 'Course Metrics Report',
    generated_at: '2019-02-21T01:23:45.123456Z',
    report_url: '#',
    report_type: 'Course Metrics Report'
  }
]


class CsvReports extends Component {
  constructor(props) {
    super(props);

    this.state = {
      fetchedAutoReports: Immutable.fromJS({
        'user-reports': [],
        'grade-reports': [],
        'course-metrics-reports': []
      }),
      displayedAutoReports: Immutable.fromJS([]),
      filterOptions: Immutable.fromJS({
        'years': [{value: 0, label: 'No filter'}],
        'months': [{value: 0, label: 'No filter'}]
      }),
      autoReportsMonthFilter: 0,
      autoReportsYearFilter: 0,
      selectedAutoReports: 'user-reports',
    };

    this.initialReportsFetch = this.initialReportsFetch.bind(this);
    this.setDisplayedAutoReports = this.setDisplayedAutoReports.bind(this);
    this.setAutoReportMonthFilter = this.setAutoReportMonthFilter.bind(this);
    this.setAutoReportYearFilter = this.setAutoReportYearFilter.bind(this);
    this.getFilterOptions = this.getFilterOptions.bind(this);
    this.setSelectedAutoReports = this.setSelectedAutoReports.bind(this);
  }

  initialReportsFetch = () => {
    const tempReports = Immutable.fromJS({
      'user-reports': UserReports,
      'grade-reports': GradeReports,
      'course-metrics-reports': CourseMetricsReports
    });
    this.setState({
      fetchedAutoReports: tempReports,
    }, () => {
      this.setDisplayedAutoReports();
      this.getFilterOptions();
    })
  }

  setDisplayedAutoReports = () => {
    const tempReports = this.state.fetchedAutoReports.get(this.state.selectedAutoReports);
    let filteredReports = Immutable.fromJS([]);
    tempReports.forEach((report, index) => {
      const generatedDate = new Date(report.get('generated_at'));
      if ((this.state.autoReportsYearFilter !== 0) && (generatedDate.getFullYear() !== this.state.autoReportsYearFilter)) {
        return
      }
      if ((this.state.autoReportsMonthFilter !== 0) && ((generatedDate.getMonth() + 1) !== this.state.autoReportsMonthFilter)) {
        return
      }
      filteredReports = filteredReports.push(report);
    })
    this.setState({
      displayedAutoReports: filteredReports,
    })
  }

  getFilterOptions = () => {
    let filterYears = Immutable.fromJS([]);
    let filterMonths = Immutable.fromJS([]);
    // go through reports and find all the unique months and years of reports
    this.state.fetchedAutoReports.get('user-reports').forEach((report, index) => {
      const generatedDate = new Date(report.get('generated_at'));
      if (!filterYears.includes(generatedDate.getFullYear())) {
        filterYears = filterYears.push(generatedDate.getFullYear());
      };
      if (!filterMonths.includes((generatedDate.getMonth() + 1))) {
        filterMonths = filterMonths.push((generatedDate.getMonth() + 1));
      };
    });
    // sort lists of retrieved years and months
    filterYears = filterYears.sort();
    filterMonths = filterMonths.sort();
    // store lists of years and months in a format that suits our selector component
    let filterYearsFull = Immutable.List([{value: 0, label: 'No filter'}]);
    let filterMonthsFull = Immutable.List([{value: 0, label: 'No filter'}]);
    filterYears.forEach((year, index) => {
      filterYearsFull = filterYearsFull.push({value: year, label: year.toString()});
    });
    filterMonths.forEach((month, index) => {
      filterMonthsFull = filterMonthsFull.push({value: month, label: monthNames[month]});
    });
    // finally, store the formatted data into the state, to be used by filter selectors
    const tempFilterOptions = Immutable.fromJS({
      years: filterYearsFull.sort(),
      months: filterMonthsFull.sort(),
    });
    this.setState({
      filterOptions: tempFilterOptions,
    });
  }

  setAutoReportMonthFilter = (payload) => {
    this.setState({
      autoReportsMonthFilter: payload.value
    }, () => this.setDisplayedAutoReports())
  }

  setAutoReportYearFilter = (payload) => {
    this.setState({
      autoReportsYearFilter: payload.value
    }, () => this.setDisplayedAutoReports())
  }

  setSelectedAutoReports = (selection) => {
    this.setState({
      selectedAutoReports: selection
    }, () => this.setDisplayedAutoReports())
  }

  componentDidMount() {
    this.initialReportsFetch();
  }

  render() {

    const displayedAutoReportsRender = this.state.displayedAutoReports.map((report, index) => {
      return (
        <li key={index} className={styles['report']}>
          <div className={styles['report-name']}>
            <Link
              to={'/figures/report/' + report.get('report_url')}
              className={styles['view-report-button']}
            >
              {report.get('report_name')}
            </Link>
          </div>
          <div className={styles['report-timestamp']}>
            {parseReportDate(report.get('generated_at'))}
          </div>
          <div className={styles['report-buttons']}>
            <Link
              to={'/figures/report/' + report.get('report_url')}
              className={styles['view-report-button']}
            >
              View report
            </Link>
          </div>
        </li>
      )
    })

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentCsvReports />
        </HeaderAreaLayout>
        <section className={cx({ 'container': true, 'csv-reports-content': true, 'csv-regular-reports-content': true})}>
          <div className={styles['reports-section']}>
            <div className={styles['reports-filters']}>
              <div className={styles['header-title']}>
                Regular automatically generated CSV reports
              </div>
              <div className={styles['filters-heading']}>
                Filter reports
              </div>
              <span className={styles['filters-heading-separator']}></span>
              <div className={styles['filter']}>
                <div className={styles['dropdown-container']}>
                  <span>Year:</span>
                  <Select
                    options={this.state.filterOptions.get('years').toJS()}
                    onChange = {this.setAutoReportYearFilter}
                    value={this.state.filterOptions.get('years').get(this.state.filterOptions.get('years').findIndex(item => (item.value === this.state.autoReportsYearFilter)))}
                  />
                </div>
              </div>
              <div className={styles['filter']}>
                <div className={styles['dropdown-container']}>
                  <span>Month:</span>
                  <Select
                    options={this.state.filterOptions.get('months').toJS()}
                    onChange = {this.setAutoReportMonthFilter}
                    value={this.state.filterOptions.get('months').get(this.state.filterOptions.get('months').findIndex(item => (item.value === this.state.autoReportsMonthFilter)))}
                  />
                </div>
              </div>
            </div>
            <div className={styles['report-tab-select']}>
              <button
                className={cx({ 'report-selector': true, 'active': (this.state.selectedAutoReports === 'user-reports')})}
                onClick={() => this.setSelectedAutoReports('user-reports')}
              >
                User Reports
              </button>
              <button
                className={cx({ 'report-selector': true, 'active': (this.state.selectedAutoReports === 'grade-reports')})}
                onClick={() => this.setSelectedAutoReports('grade-reports')}
              >
                Grade Reports
              </button>
              <button
                className={cx({ 'report-selector': true, 'active': (this.state.selectedAutoReports === 'course-metrics-reports')})}
                onClick={() => this.setSelectedAutoReports('course-metrics-reports')}
              >
                Course Metrics Reports
              </button>
            </div>
            <ul className={styles['reports-list']}>
              <li key='list-header' className={cx(styles['report'], styles['list-header'])}>
                <div className={styles['report-name']}>
                  Report name:
                </div>
                <div className={styles['report-timestamp']}>
                  Time created:
                </div>
                <div className={styles['report-buttons']}>
                </div>
              </li>
              {displayedAutoReportsRender}
            </ul>
          </div>
        </section>
      </div>
    );
  }
}

export default CsvReports;
