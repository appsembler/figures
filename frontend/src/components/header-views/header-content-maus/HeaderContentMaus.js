import React, { Component } from 'react';
import Immutable from 'immutable';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import classNames from 'classnames/bind';
import styles from './_header-content-maus.scss';
import { ResponsiveContainer, AreaChart, Area, Tooltip } from 'recharts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faAngleDoubleUp, faAngleDoubleDown } from '@fortawesome/free-solid-svg-icons';

let cx = classNames.bind(styles);

class CustomTooltip extends Component {

  render() {
    const { active } = this.props;

    if (active) {
      const { payload } = this.props;
      return (
        <div className={styles['bar-tooltip']}>
          <span className={styles['tooltip-value']}>{payload[0].value}</span>
          <p>active users in {payload[0].payload.period}</p>
        </div>
      );
    }

    return null;
  }
}

class HeaderContentMaus extends Component {
  render() {
    let currentPeriodValue = this.props.mauDataCurrent;
    let previousPeriodValue = this.props.mauDataHistory.getIn([this.props.mauDataHistory.size-2, 'value'], 0);
    let comparisonIcon;
    let comparisonValue;
    if (currentPeriodValue >= previousPeriodValue) {
      comparisonIcon = <FontAwesomeIcon icon={faAngleDoubleUp} />;
      comparisonValue = currentPeriodValue - previousPeriodValue;
    } else {
      comparisonIcon = <FontAwesomeIcon icon={faAngleDoubleDown} />;
      comparisonValue = previousPeriodValue - currentPeriodValue;
    }

    return (
      <section className={styles['header-content-maus']}>
        <div className={cx({ 'main-content': true, 'container': true})}>
          <div className={styles['users-count']}>
            <span className={styles['number']}>{currentPeriodValue}</span>
            <span className={styles['text']}>active users (MAUs) this month</span>
          </div>
          <span className={styles['text-separator']} />
          <div className={styles['comparison-box']}>
            <span className={styles['comparison-box__icon']}>{comparisonIcon}</span>
            <span className={styles['comparison-box__text']}>
              {(currentPeriodValue >= previousPeriodValue) ? 'up' : 'down'} {comparisonValue} compared to last month
            </span>
            {this.props.showHistoryButton ? (
              <Link to='/figures/mau-history' className={styles['mau-history-link']}>See details</Link>
            ) : ''}
          </div>
        </div>
        <div className={styles['graph-container']}>
          <ResponsiveContainer width="100%" height={110}>
            {this.props.mauDataHistory.size ? (
              <AreaChart
                data={this.props.mauDataHistory.toJS()}
                margin={{top: 0, bottom: 0, left: 0, right: 0}}
              >
                <Area type='linear' dataKey='value' stroke='none' fill='#ffffff' fillOpacity={0.8} />
                <Tooltip
                  content={<CustomTooltip/>}
                  cursor={{ fill: 'rgba(255, 255, 255, 0.15)'}}
                  offset={0}
                />
              </AreaChart>
            ) : (
              <span className={styles['no-data-label']}>Active Users historic data unavailable</span>
            )}
          </ResponsiveContainer>
        </div>
      </section>
    );
  }
}

HeaderContentMaus.defaultProps = {
  showHistoryButton: false
}

const mapStateToProps = (state, ownProps) => ({
  mauDataCurrent: Immutable.fromJS(state.generalData.activeUsers['current_month']),
  mauDataHistory: Immutable.fromJS(state.generalData.activeUsers['history']),
})

export default connect(
  mapStateToProps,
)(HeaderContentMaus)
