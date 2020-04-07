import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Immutable from 'immutable';
import styles from './_base-stat-card.scss';
import classNames from 'classnames/bind';
import StatBarGraph from 'base/components/stat-graphs/stat-bar-graph/StatBarGraph';

let cx = classNames.bind(styles);


class BaseStatCard extends Component {
  constructor(props) {
    super(props);

    this.state = {
      historyExpanded: false,
      cardWidth: this.props.cardWidth,
      mainValue: (this.props.dataType === 'number') ? 0 : '-',
      valueHistory: Immutable.fromJS([]),
      comparisonValue: '-',
    };

    this.historyToggle = this.historyToggle.bind(this);
  }

  historyToggle = () => {
    this.setState({
      historyExpanded: !this.state.historyExpanded,
      cardWidth: this.state.historyExpanded ? 1 : 4,
    });
  }

  calculateComparisonValue = () => {
    if (this.props.compareToPrevious && !this.props.singleValue && this.state.valueHistory.size) {
      if (this.props.dataType === 'percentage') {
        this.setState({
          comparisonValue: `${((this.state.mainValue - this.state.valueHistory.getIn([this.state.valueHistory.size-2, 'value']))*100).toFixed(2)}%`,
        })
      } else {
        this.setState({
          comparisonValue: `${this.state.mainValue - this.state.valueHistory.getIn([this.state.valueHistory.size-2, 'value'])}`,
        })
      }
    }
  }

  initialDataSet = () => {
    if (this.props.fetchValueFunction && this.props.fetchDataKey) {
      this.props.fetchValueFunction(this.props.fetchDataKey).then((response) => {
        if (response.error) {
          console.log(`Error fetching the ${this.props.cardTitle} data: ${response.error}`)
        } else {
          const responseData = Immutable.fromJS(response);
          this.setState({
            mainValue: this.props.mainValue ? this.props.mainValue : responseData.getIn([this.props.fetchDataKey, this.props.dataMainValueKey], this.state.mainValue),
            valueHistory: this.props.valueHistory ? this.props.valueHistory : responseData.getIn([this.props.fetchDataKey, this.props.dataHistoryKey], this.state.valueHistory),
          }, () => {
            this.calculateComparisonValue();
          })
        }
      })
    } else {
      this.setState({
        mainValue: this.props.mainValue ? this.props.mainValue : this.state.mainValue,
        valueHistory: this.props.valueHistory ? this.props.valueHistory : this.state.valueHistory,
      }, () => {
        this.calculateComparisonValue();
      })
    }
  }

  componentDidMount() {
    this.initialDataSet();
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    if (this.props !== nextProps) {
      this.setState({
        mainValue: nextProps.mainValue ? nextProps.mainValue : this.state.mainValue,
        valueHistory: nextProps.valueHistory ? nextProps.valueHistory : this.state.valueHistory,
      }, () => {
        this.calculateComparisonValue();
      })
    }
  }

  component

  render() {

    return (
      <div className={cx({ 'stat-card': true, 'span-2': (this.state.cardWidth === 2), 'span-3': (this.state.cardWidth === 3), 'span-4': (this.state.cardWidth === 4)})}>
        <div className={styles['main-content']}>
          <span className={styles['card-title']}>{this.props.cardTitle}</span>
          {(this.props.cardDescription !== '') && (
            <span className={styles['card-description']}>
              {this.props.cardDescription}
            </span>
          )}
          <div className={styles['main-data-container']}>
            {this.props.singleValue ? (
              <span className={styles['current-data']}>{this.state.mainValue}</span>
            ) : (
              <span className={styles['current-data']}>{(this.props.dataType === 'percentage') ? ((this.state.mainValue)*100).toFixed(2) : (this.state.mainValue)}{(this.props.dataType === 'percentage') && '%'}</span>
            )}
            {(this.props.compareToPrevious && !this.props.singleValue) && (
              <div className={styles['previous-comparison']}>
                <span className={styles['comparison-value']}>{this.state.comparisonValue}</span>
                <span className={styles['comparison-text']}>since last month</span>
              </div>
            )}
          </div>
          {(this.props.enableHistory && !this.props.singleValue) ? (
            <button onClick={this.historyToggle} className={styles['history-toggle']}>{this.state.historyExpanded ? 'hide history' : 'see history'}</button>
          ) : (
            <span className={styles['history-toggle-faux']}></span>
          )}
        </div>
        {(this.state.historyExpanded && this.props.enableHistory) && (
          <div className={styles['history-content']}>
            <StatBarGraph
              data={this.state.valueHistory}
              graphHeight='100%'
              dataType={this.props.dataType}
            />
          </div>
        )}
      </div>
    )
  }
}

BaseStatCard.defaultProps = {
  cardTitle: 'Test stat title',
  cardDescription: '',
  cardWidth: 1,
  compareToPrevious: true,
  dataType: 'number',
  enableHistory: true,
  singleValue: false,
  dataMainValueKey: 'current_month',
  dataHistoryKey: 'history',
}

BaseStatCard.propTypes = {
  cardTitle: PropTypes.string,
  cardDescription: PropTypes.string,
  cardWidth: PropTypes.number,
  dataType: PropTypes.string,
  mainValue: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  compareToPrevious: PropTypes.bool,
  enableHistory: PropTypes.bool,
  singleValue: PropTypes.bool,
  valueHistory: PropTypes.object,
  fetchDataFunction: PropTypes.func,
  fetchDataKey: PropTypes.string,
  dataMainValueKey: PropTypes.string,
  dataHistoryKey: PropTypes.string,
};

export default BaseStatCard;
