import React from 'react';
import styles from './_loading-spinner.scss';
import { HashLoader } from 'react-spinners';
import { usePromiseTracker } from "react-promise-tracker";
import classNames from 'classnames/bind';

let cx = classNames.bind(styles);

const appsemblerBlue = '#0090c1';

const LoadingSpinner = props => {

  const { promiseInProgress } = usePromiseTracker();

  return (
    <section className={styles['loading-spinner-root-container']}>
      {promiseInProgress && (
        <div className={styles['spinner-container']}>
          <div className={styles['spinner-container__content']}>
            <HashLoader
              color={appsemblerBlue}
            />
            <span>Loading your data...</span>
          </div>
        </div>
      )}
      <div className={cx({ 'main-content': true, 'blurred': promiseInProgress })}>
        {props.children}
      </div>
    </section>
  )
}

export default LoadingSpinner;
