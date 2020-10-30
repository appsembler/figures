import React, { Component } from 'react';
import classNames from 'classnames/bind';
import { connect } from 'react-redux';
import styles from './_mau-details-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/header-content-maus/HeaderContentMaus';

let cx = classNames.bind(styles);


class MauDetailsContent extends Component {

  render() {
    let previousValue = undefined;
    const mausRender = this.props.mauHistory.map((period, index) => {
      const difference = (previousValue || (previousValue == 0)) ? (period.value - previousValue) : 'N/A';
      previousValue = period.value;
      return (
        <li key={index} className={styles['content-row']}>
          <span className={styles['period']}>{period.period}</span>
          <span className={styles['mau-count']}>{period.value}</span>
          <span className={cx({ 'difference': true, 'positive': ((difference > 0) || (difference === undefined)), 'negative': (difference < 0)})}>{(difference > 0) ? "+" : ""}{difference}</span>
        </li>
      )
    });

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentMaus />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'mau-details-content': true})}>
          <section className={styles['mau-history-list']}>
            <div className={styles['header']}>
              <div className={styles['header-title']}>
                Monthly Active Users history
              </div>
            </div>
            <div className={cx({ 'stat-card': true, 'span-2': false, 'span-3': false, 'span-4': true, 'mau-table-container': true})}>
              <ul className={styles['mau-table']}>
                <li key="header" className={styles['header-row']}>
                  <span className={styles['period']}>Period</span>
                  <span className={styles['mau-count']}>Monthly active users</span>
                  <span className={styles['difference']}>Difference vs. previous period</span>
                </li>
                {mausRender.reverse()}
              </ul>
            </div>
          </section>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  mauHistory: state.generalData.activeUsers['history']
})

export default connect(
  mapStateToProps,
)(MauDetailsContent)
