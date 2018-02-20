import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import classNames from 'classnames/bind';
import styles from 'base/sass/header-views/_header-content-maus.scss';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import { faAngleDoubleUp, faAngleDoubleDown } from '@fortawesome/fontawesome-free-solid';

let cx = classNames.bind(styles);

class HeaderContentMaus extends Component {
  render() {
    let currentPeriodValue = this.props.data[this.props.data.length-1].value;
    let previousPeriodValue = this.props.data[this.props.data.length-2].value;
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
            <Link to='test' className={styles['mau-history-link']}>See history</Link>
          </div>
        </div>
        <div className={styles['graph-container']}>
          <ResponsiveContainer width="100%" height={110}>
            <AreaChart
              data={this.props.data}
              margin={{top: 0, bottom: 0, left: 0, right: 0}}
            >
              <Area type='linear' dataKey='value' stroke='none' fill='#ffffff' fillOpacity={0.8} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>
    );
  }
}

HeaderContentMaus.defaultProps = {
  data: [
    {
      timePeriodName: 'January',
      value: 1420
    },
    {
      timePeriodName: 'February',
      value: 2900
    },
    {
      timePeriodName: 'March',
      value: 401
    },
    {
      timePeriodName: 'April',
      value: 1180
    },
    {
      timePeriodName: 'May',
      value: 1910
    }
  ]
}

export default HeaderContentMaus;
