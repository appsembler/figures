import React, { Component } from 'react';
import { List } from 'immutable';
import PropTypes from 'prop-types';
import styles from './_learner-statistics.scss';
import classNames from 'classnames/bind';
import Select from 'react-select';
import StatHorizontalBarGraph from 'base/components/stat-graphs/stat-bar-graph/StatHorizontalBarGraph';

let cx = classNames.bind(styles);

var countries = require("i18n-iso-countries");
countries.registerLocale(require("i18n-iso-countries/langs/en.json"));

class LearnerStatistics extends Component {
  constructor(props) {
    super(props);
    this.state = {
      breakdownType: this.props.breakdownType,
      graphData: [],
      countryStats: List([
        {
          value: "n-a",
          label: "Not available",
          count: 0
        }
      ]),
      genderStats: List([
        {
          value: "m",
          label: "Male",
          count: 0
        },
        {
          value: "f",
          label: "Female",
          count: 0
        },
        {
          value: "o",
          label: "Other / Prefer not to say",
          count: 0
        }
      ]),
      educationLevelStats: List([
        {
          value: "p",
          label: "PhD or Doctorate",
          count: 0
        },
        {
          value: "m",
          label: "Master's or professional degree",
          count: 0
        },
        {
          value: "b",
          label: "Bachelor's degree",
          count: 0
        },
        {
          value: "a",
          label: "Associate's degree",
          count: 0
        },
        {
          value: "hs",
          label: "Secondary/high school",
          count: 0
        },
        {
          value: "jhs",
          label: "Junior secondary/junior high/middle school",
          count: 0
        },
        {
          value: "none",
          label: "None",
          count: 0
        },
        {
          value: "o",
          label: "Other",
          count: 0
        },
        {
          value: "n-a",
          label: "Not available",
          count: 0
        }
      ])
    };
    this.onChangeBreakdownType = this.onChangeBreakdownType.bind(this);
    this.retrieveData = this.retrieveData.bind(this);
    this.analyzeData = this.analyzeData.bind(this);
  }

  onChangeBreakdownType = (payload) => {
    this.setState({
      breakdownType: payload.value,
    }, () => {
      this.retrieveData(payload.value);
    });
  }

  analyzeData = (learnersData) => {
    let countryStats = this.state.countryStats;
    let genderStats = this.state.genderStats;
    let educationLevelStats = this.state.educationLevelStats;
    learnersData.forEach((learner, index) => {
      //country
      const learnerCountryTemp = learner.getIn(['country']) ? learner.getIn(['country']) : 'n-a';
      let foundIndex = countryStats.findIndex(item => (item.value === learnerCountryTemp));
      if (foundIndex !== -1) {
        countryStats = countryStats.set(foundIndex, { value: learnerCountryTemp, label: (learnerCountryTemp !== 'n-a') ? countries.getName(learnerCountryTemp, "en") : "Not available", count: countryStats.get(foundIndex).count + 1 });
      } else {
        countryStats = countryStats.push({ value: learnerCountryTemp, label: (learnerCountryTemp !== 'n-a') ? countries.getName(learnerCountryTemp, "en") : "Not available", count: 1 })
      }
      //gender
      const genderTemp = learner.getIn(['gender']) ? learner.getIn(['gender']) : 'n-a';
      foundIndex = genderStats.findIndex(item => (item.value === genderTemp));
      genderStats = genderStats.set(foundIndex, { value: genderTemp, label: genderStats.get(foundIndex).label, count: genderStats.get(foundIndex).count + 1 });
      //education
      const educationLevelTemp = learner.getIn(['level_of_education']) ? learner.getIn(['level_of_education']) : 'n-a';
      foundIndex = educationLevelStats.findIndex(item => (item.value === educationLevelTemp));
      educationLevelStats = educationLevelStats.set(foundIndex, { value: educationLevelTemp, label: educationLevelStats.get(foundIndex).label, count: educationLevelStats.get(foundIndex).count + 1 });
    })
    this.setState({
      countryStats: countryStats.sortBy(item => item.count).reverse(),
      genderStats: genderStats.sortBy(item => item.count).reverse(),
      educationLevelStats: educationLevelStats.sortBy(item => item.count).reverse()
    }, () => this.retrieveData(this.props.breakdownType))
  }

  retrieveData = (parameter) => {
    if (parameter === 'gender') {
      this.setState({
        graphData: this.state.genderStats.toArray()
      })
    } else if (parameter === 'country') {
      this.setState({
        graphData: this.state.countryStats.toArray()
      })
    } else if (parameter === 'education') {
      this.setState({
        graphData: this.state.educationLevelStats.toArray()
      })
    }
  }

  componentWillReceiveProps = (nextProps) => {
    this.analyzeData(nextProps.learnersData);
  }

  componentDidMount() {
    this.analyzeData(this.props.learnersData);
  }

  render() {
    const dropdownOptions = List([
      { value: 'education', label: 'By education level' },
      { value: 'gender', label: 'By gender' },
      { value: 'country', label: 'By country' },
    ])

    return (
      <section className={styles['courses-list']}>
        <div className={styles['header']}>
          <div className={styles['header-title']}>
            {this.props.listTitle}
          </div>
          <div className={styles['dropdown-container']}>
            <span>Course learners breakdown type:</span>
            <Select
              options={dropdownOptions.toArray()}
              onChange = {this.onChangeBreakdownType}
              value={dropdownOptions.get(dropdownOptions.findIndex(item => (item.value === this.state.breakdownType)))}
            />
          </div>
        </div>
        <div className={cx({ 'stat-card': true, 'span-2': false, 'span-3': false, 'span-4': true})}>
          <StatHorizontalBarGraph
            data={this.state.graphData}
            valueLabel='count'
            labelLabel='label'
          />
        </div>
      </section>
    )
  }
}

LearnerStatistics.defaultProps = {
  listTitle: 'Learner statistics:',
  breakdownType: 'country',
}

LearnerStatistics.propTypes = {
  listTitle: PropTypes.string,
  getIdListFunction: PropTypes.func,
  getCourseDataFunction: PropTypes.func,
  breakdownType: PropTypes.string,
};

export default LearnerStatistics;
