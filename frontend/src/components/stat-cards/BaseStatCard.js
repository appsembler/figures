import React, { Component } from 'react';
import PropTypes from 'prop-types';
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
    let mainData = this.props.getDataFunction(this.props.dataParameter, 2);

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
              <span className={styles['current-data']}>{this.props.value}</span>
            ) : (
              <span className={styles['current-data']}>{(this.props.dataType === 'percentage') ? (mainData[1].value)*100 : (mainData[1].value)}{(this.props.dataType === 'percentage') && '%'}</span>
            )}
            {(this.props.compareToPrevious && !this.props.singleValue) && (
              <div className={styles['previous-comparison']}>
                <span className={styles['comparison-value']}>{(this.props.dataType === 'percentage') ? (((mainData[1].value - mainData[0].value)*100).toFixed(2)) : (mainData[1].value - mainData[0].value)}{(this.props.dataType === 'percentage') && '%'}</span>
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
              data={this.props.getDataFunction(this.props.dataParameter, 12)}
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
  cardDescription: 'Leverage agile frameworks to provide a robust synopsis for high level overviews. Iterative approaches to corporate strategy foster collaborative thinking to further the overall value proposition.',
  cardWidth: 1,
  compareToPrevious: true,
  dataType: 'number',
  enableHistory: true,
  singleValue: false,
  value: '',
}

BaseStatCard.propTypes = {
  cardTitle: PropTypes.string,
  cardDescription: PropTypes.string,
  cardWidth: PropTypes.number,
  dataType: PropTypes.string,
  getDataFunction: PropTypes.func,
  dataParameter: PropTypes.string,
  compareToPrevious: PropTypes.bool,
  enableHistory: PropTypes.bool,
  singleValue: PropTypes.bool,
  value: PropTypes.string,
};

export default BaseStatCard;
