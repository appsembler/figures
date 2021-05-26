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
          Résumé
        </NavLink>
        <NavLink
          to="/figures/mau-history"
          className={styles['header-nav__link']}
        >
          Mensuel
        </NavLink>
        <NavLink
          to="/figures/users"
          className={styles['header-nav__link']}
        >
          Utilisateurs
        </NavLink>
        <NavLink
          to="/figures/courses"
          className={styles['header-nav__link']}
        >
          Cours
        </NavLink>
        <NavLink
          to="/figures/learners-progress-overview"
          className={styles['header-nav__link']}
        >
          Aperçu progrès
        </NavLink>
        {(process.env.ENABLE_CSV_REPORTS === "enabled") && (
          <NavLink
            to="/figures/csv-reports"
            className={styles['header-nav__link']}
          >
            Rapports CSV
          </NavLink>
        )}
        <AutoCompleteCourseSelect
          negativeStyleButton
          buttonText='Recherche cours'
        />
        <AutoCompleteUserSelect
          negativeStyleButton
          buttonText='Recherche utilisateur'
        />
      </div>
    );
  }
}

export default HeaderNav
