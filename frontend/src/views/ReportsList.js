import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchReportsList } from 'base/redux/actions/Actions';
import styles from './_reports-list-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentReportsList from 'base/components/header-views/header-content-reports-list/HeaderContentReportsList';

import classNames from 'classnames/bind';
let cx = classNames.bind(styles);


class ReportsList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      reportsList: this.props.reportsList,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props !== nextProps) {
      this.setState({
        reportsList: nextProps.reportsList,
      })
    }
  }

  componentDidMount() {
    this.props.fetchReportsList(this.props.userId)
  }

  render() {
    const listItems = this.state.reportsList.map((report, index) => {
      return (
        <li key={index} className={styles['report']}>
          <div className={styles['report-name']}>
            <Link
              to={'/figures/report/' + report.reportId}
              className={styles['view-report-button']}
            >
              {report.reportName}
            </Link>
          </div>
          <div className={styles['report-description']}>
            {report.reportDescription}
          </div>
          <div className={styles['report-timestamp']}>
            {report.dateCreated}
          </div>
          <div className={styles['report-buttons']}>
            <Link
              to={'/figures/report/' + report.reportId}
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
          <HeaderContentReportsList />
        </HeaderAreaLayout>
        <ul className={cx({ 'container': true, 'reports-list': true})}>
          <li key='list-header' className={cx(styles['report'], styles['list-header'])}>
            <div className={styles['report-name']}>
              Report name:
            </div>
            <div className={styles['report-description']}>
              Report description:
            </div>
            <div className={styles['report-timestamp']}>
              Time created:
            </div>
            <div className={styles['report-buttons']}>
            </div>
          </li>
          {listItems}
        </ul>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  userId: state.userData.userId,
  reportsList: state.reportsList.reportsData,
})

const mapDispatchToProps = dispatch => ({
  fetchReportsList: userId => dispatch(fetchReportsList(userId)),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ReportsList)
