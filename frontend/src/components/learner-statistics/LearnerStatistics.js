import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styles from './_learner-statistics.scss';
import classNames from 'classnames/bind';
import Select from 'react-select';
import StatHorizontalBarGraph from 'base/components/stat-graphs/stat-bar-graph/StatHorizontalBarGraph';

let cx = classNames.bind(styles);

class LearnerStatistics extends Component {
  constructor(props) {
    super(props);
    this.state = {
      breakdownType: this.props.breakdownType,
      graphData: [],
    };
    this.onChangeBreakdownType = this.onChangeBreakdownType.bind(this);
    this.retrieveData = this.retrieveData.bind(this);

  }

  onChangeBreakdownType = (payload) => {
    this.setState({
      breakdownType: payload.value,
    }, () => {
      this.retrieveData(payload.value);
    });
  }

  retrieveData = (parameter) => {
    const testDataGender = [
      {
        value: 0.6,
        label: 'Female',
      },
      {
        value: 0.35,
        label: 'Male',
      },
      {
        value: 0.05,
        label: 'Other',
      }
    ];
    const testDataCountry = [
      {
        value: 0.45,
        label: 'USA',
      },
      {
        value: 0.35,
        label: 'Great Britain',
      },
      {
        value: 0.05,
        label: 'Canada',
      },
      {
        value: 0.08,
        label: 'Croatia',
      },
      {
        value: 0.02,
        label: 'France',
      },
      {
        value: 0.05,
        label: 'Other',
      }
    ]
    console.log('Calling API for: ', parameter);
    if (parameter === 'gender') {
      this.setState({
        graphData: testDataGender,
      })
    } else if (parameter === 'country') {
      this.setState({
        graphData: testDataCountry,
      })
    }
  }

  componentDidMount() {
    this.retrieveData(this.props.breakdownType);
  }

  render() {
    const dropdownOptions = [
      { value: 'gender', label: 'By gender' },
      { value: 'country', label: 'By country' }
    ]

    return (
      <section className={styles['courses-list']}>
        <div className={styles['header']}>
          <div className={styles['header-title']}>
            {this.props.listTitle}
          </div>
          <div className={styles['dropdown-container']}>
            <span>Course learners breakdown type:</span>
            <Select
              options={dropdownOptions}
              onChange = {this.onChangeBreakdownType}
              value={dropdownOptions[0]}
            />
          </div>
        </div>
        <div className={cx({ 'stat-card': true, 'span-2': false, 'span-3': false, 'span-4': true})}>
          <StatHorizontalBarGraph
            data={this.state.graphData}
            dataType='percentage'
          />
        </div>
      </section>
    )
  }
}

LearnerStatistics.defaultProps = {
  listTitle: 'Learner statistics:',
  breakdownType: 'gender',
}

LearnerStatistics.propTypes = {
  listTitle: PropTypes.string,
  getIdListFunction: PropTypes.func,
  getCourseDataFunction: PropTypes.func,
  breakdownType: PropTypes.string,
};

export default LearnerStatistics;
