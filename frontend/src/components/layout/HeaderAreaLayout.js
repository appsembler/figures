import React, { Component } from 'react';
import classNames from 'classnames/bind';
import PropTypes from 'prop-types';
import styles from './_header-area-layout.scss';
import HeaderNav from 'base/components/layout/HeaderNav';
import figuresLogo from 'base/images/logo/edx-figures--logo--negative.svg';

let cx = classNames.bind(styles);

class HeaderAreaLayout extends Component {

  render() {

    return (
      <div className={styles['header-area']}>
        <div className={cx({ 'header-top': true, 'container': true })}>
          <div className={styles['header-logo-container']}>
            <img src={figuresLogo} alt="EdX Figures" role="presentation" />
          </div>
          <HeaderNav />
        </div>
        {this.props.children}
      </div>
    );
  }
}

HeaderAreaLayout.propTypes = {
  children: PropTypes.node,
}

export default HeaderAreaLayout;
