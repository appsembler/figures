import React, { Component } from 'react';
import PropTypes from 'prop-types';
import styles from 'base/sass/layouts/_header-area-layout.scss';
import HeaderNav from 'base/components/layout/HeaderNav';
import figuresLogo from 'base/images/logo/edx-figures--logo--negative.svg';

class HeaderAreaLayout extends Component {
  render() {
    return (
      <div className={styles.header_area}>
        <div className="ef--container ef--header-top">
          <div className="ef--header-logo"><img src={figuresLogo} alt="edX Figures" role="presentation" /></div>
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
