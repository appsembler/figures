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
          Overview
        </NavLink>
        <NavLink
          to="/figures/mau-history"
          className={styles['header-nav__link']}
        >
          MAU History
        </NavLink>
        <NavLink
          to="/figures/users"
          className={styles['header-nav__link']}
        >
          Users
        </NavLink>
        <NavLink
          to="/figures/courses"
          className={styles['header-nav__link']}
        >
          Courses
        </NavLink>
        <NavLink
          to="/figures/learners-progress-overview"
          className={styles['header-nav__link']}
        >
          Learners Progress Overview
        </NavLink>
        {(process.env.ENABLE_CSV_REPORTS === "enabled") && (
          <NavLink
            to="/figures/csv-reports"
            className={styles['header-nav__link']}
          >
            CSV Reports
          </NavLink>
        )}
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
