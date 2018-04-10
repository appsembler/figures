import React, { Component } from 'react';
import classNames from 'classnames/bind';
import styles from './_single-report-content.scss';
import ContentEditable from 'base/components/inputs/ContentEditable'

let cx = classNames.bind(styles);


class SingleCourseContent extends Component {
  constructor(props) {
    super(props);

    this.state = {

    };
  }

  render() {
    return (
      <div className={cx({ 'container': true, 'base-grid-layout': true, 'report-content': true})}>
        <div className={styles['content-meta']}>
          <div className={styles['meta-description']}>
            <span className={styles['meta-heading']}>
              About this report:
            </span>
          </div>
          <div className={styles['meta-date']}>
            <span className={styles['meta-heading']}>
              Date created:
            </span>
            <span className={styles['meta-content']}>
              12/22/2017
            </span>
          </div>
          <div className={styles['meta-author']}>
            <span className={styles['meta-heading']}>
              Created by:
            </span>
            <span className={styles['meta-content']}>
              Name Surname
            </span>
          </div>
        </div>
      </div>
    );
  }
}

export default SingleCourseContent;
