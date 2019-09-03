
import React, { Component } from 'react';
import classNames from 'classnames/bind';
import styles from './_header-content-csv-reports.scss';

let cx = classNames.bind(styles);

class HeaderContentCsvReports extends Component {
  render() {

    return (
      <section className={cx({ 'header-content-reports-list': true, 'container': true})}>
        <div className={styles['title-container']}>
          <div className={styles['title-text']}>CSV Downloadable Reports</div>
          <div className={styles['subtitle-text']}>Download sets of your site data in CSV format.</div>
          <span className={styles['title-decoration']} />
        </div>
      </section>
    );
  }
}

HeaderContentCsvReports.defaultProps = {

}

export default HeaderContentCsvReports;
