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
    };

    this.historyToggle = this.historyToggle.bind(this);
  }

  historyToggle = () => {
    if (this.state.historyExpanded) {
      this.setState({
        historyExpanded: false,
        cardWidth: 1
      }, () => {

      });
    } else {
      this.setState({
        historyExpanded: true,
        cardWidth: 4
      }, () => {

      });
    }
  }

  render() {
    const valueHistory = this.props.valueHistory.length ? this.props.valueHistory : Immutable.fromJS([ { period: '', value: 0 }, { period: '', value: 0 } ])

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
              <span className={styles['current-data']}>{this.props.mainValue}</span>
            ) : (
              <span className={styles['current-data']}>{(this.props.dataType === 'percentage') ? ((this.props.mainValue)*100).toFixed(2) : (this.props.mainValue)}{(this.props.dataType === 'percentage') && '%'}</span>
            )}
            {(this.props.compareToPrevious && !this.props.singleValue) && (
              <div className={styles['previous-comparison']}>
                <span className={styles['comparison-value']}>{(this.props.dataType === 'percentage') ? (((this.props.mainValue - valueHistory.getIn([valueHistory.size-2, 'value']))*100).toFixed(2)) : (this.props.mainValue - valueHistory.getIn([valueHistory.size-2, 'value']))}{(this.props.dataType === 'percentage') && '%'}</span>
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
              data={this.props.valueHistory}
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
  mainValue: 0,
  valueHistory: []
}

BaseStatCard.propTypes = {
  cardTitle: PropTypes.string,
  cardDescription: PropTypes.string,
  cardWidth: PropTypes.number,
  dataType: PropTypes.string,
  mainValue: PropTypes.number,
  compareToPrevious: PropTypes.bool,
  enableHistory: PropTypes.bool,
  singleValue: PropTypes.bool,
  valueHistory: PropTypes.array
};

export default BaseStatCard;
