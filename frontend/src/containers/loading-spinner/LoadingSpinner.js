import React, { Component } from 'react';
import styles from './_loading-spinner.scss';
import { HashLoader } from 'react-spinners';
import classNames from 'classnames/bind';

let cx = classNames.bind(styles);

class LoadingSpinner extends Component {

  render() {

    return (
      <section className={styles['loading-spinner-root-container']}>
        {this.props.displaySpinner && (
          <div className={styles['spinner-container']}>
            <div className={styles['spinner-container__content']}>
              <HashLoader
                color={'#0090c1'}
              />
              <span>Loading your data...</span>
            </div>
          </div>
        )}
        <div className={cx({ 'main-content': true, 'blurred': this.props.displaySpinner })}>
          {this.props.children}
        </div>
      </section>
    )
  }
}

export default LoadingSpinner;
