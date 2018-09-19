import React, { Component } from 'react';
import classNames from 'classnames/bind';
import PropTypes from 'prop-types';
import styles from './_header-area-layout.scss';
import HeaderNav from 'base/components/layout/HeaderNav';
import { NavLink } from 'react-router-dom';
import figuresLogo from 'base/images/logo/figures--logo--negative.svg';

let cx = classNames.bind(styles);

class HeaderAreaLayout extends Component {

  render() {

    return (
      <div className={styles['header-area']}>
        <div className={cx({ 'header-top': true, 'container': true })}>
          <NavLink
            to="/figures"
            className={styles['header-logo-container']}
          >
            <img src={figuresLogo} alt="Figures" role="presentation" />
          </NavLink>
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
