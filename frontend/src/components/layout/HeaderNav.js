import React, { Component } from 'react';
import { connect } from 'react-redux';
import { fetchCoursesIndex, fetchUserIndex, fetchGeneralData } from 'base/redux/actions/Actions';
import { NavLink } from 'react-router-dom';
import styles from './_header-nav.scss';
import AutoCompleteCourseSelect from 'base/components/inputs/AutoCompleteCourseSelect';

class HeaderNav extends Component {

  componentDidMount() {
    this.props.fetchCoursesIndex();
    this.props.fetchUserIndex();
    this.props.fetchGeneralData();
  }

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

const mapStateToProps = (state, ownProps) => ({

})

const mapDispatchToProps = dispatch => ({
  fetchCoursesIndex: () => dispatch(fetchCoursesIndex()),
  fetchUserIndex: () => dispatch(fetchUserIndex()),
  fetchGeneralData: () => dispatch(fetchGeneralData()),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(HeaderNav)
