import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import styles from './_header-nav.scss';
import AutoCompleteCourseSelect from 'base/components/inputs/AutoCompleteCourseSelect';

class HeaderNav extends Component {

  render() {
    return (
      <div className={styles['header-nav']}>
        <NavLink
          to="/figures"
          className={styles['header-nav__link']}
        >
          Dashboard
        </NavLink>
        <NavLink
          to="/figures/reports"
          className={styles['header-nav__link']}
        >
          Reports
        </NavLink>
        <AutoCompleteCourseSelect
          negativeStyleButton
          buttonText='Jump to a course'
        />
      </div>
    );
  }
}

export default HeaderNav
