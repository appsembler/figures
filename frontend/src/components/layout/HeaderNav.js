import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import styles from './_header-nav.scss';
import AutoCompleteCourseSelect from 'base/components/inputs/AutoCompleteCourseSelect';
import AutoCompleteUserSelect from 'base/components/inputs/AutoCompleteUserSelect';

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
          to="/figures/mau-history"
          className={styles['header-nav__link']}
        >
          MAU History
        </NavLink>
        <AutoCompleteCourseSelect
          negativeStyleButton
          buttonText='Jump to a course'
        />
        <AutoCompleteUserSelect
          negativeStyleButton
          buttonText='Select a user'
        />
      </div>
    );
  }
}

export default HeaderNav
