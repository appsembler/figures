import React, { Component } from 'react';
import { connect } from 'react-redux';
import { addActiveApiFetch, removeActiveApiFetch } from 'base/redux/actions/Actions';
import classNames from 'classnames/bind';
import styles from './_single-user-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentUser from 'base/components/header-views/header-content-user/HeaderContentUser';
import UserCoursesList from 'base/components/user-courses-list/UserCoursesList';
import apiConfig from 'base/apiConfig';

var countries = require("i18n-iso-countries");
countries.registerLocale(require("i18n-iso-countries/langs/en.json"));

const educationLevelsDict = {
  "p": "PhD or Doctorate",
  "m": "Master's or professional degree",
  "b": "Bachelor's degree",
  "a": "Associate's degree",
  "hs": "Secondary/high school",
  "jhs": "Junior secondary/junior high/middle school",
  "none": "None",
  "o": "Other",
  "n-a": "Not available"
}

const genderDict = {
  "m": "Male",
  "f": "Female",
  "o": "Other / Prefer not to say"
}

let cx = classNames.bind(styles);

class SingleUserContent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      userData: {}
    };

    this.fetchUserData = this.fetchUserData.bind(this);
  }

  fetchUserData = () => {
    this.props.addActiveApiFetch();
    fetch((apiConfig.learnersDetailed + this.props.userId + '/'), { credentials: "same-origin" })
      .then(response => response.json())
      .then(json => this.setState({
        userData: json
      }, () => this.props.removeActiveApiFetch()))
  }

  componentDidMount() {
    this.fetchUserData();
  }

  render() {
    const dateJoined = new Date(this.state.userData['date_joined']);
    console.log("UserData:", this.state.userData)

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentUser
            image = {this.state.userData['profile_image'] ? this.state.userData['profile_image']['image_url_large'] : ''}
            name = {this.state.userData['name']}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'user-content': true})}>
          <div className={styles['user-information']}>
            <div className={styles['name']}>
              {this.state.userData['name']}
            </div>
            <ul className={styles['user-details']}>
              <li>
                <span className={styles['label']}>Username:</span>
                <span className={styles['value']}>{this.state.userData['username']}</span>
              </li>
              <li>
                <span className={styles['label']}>Year of birth:</span>
                <span className={styles['value']}>{this.state.userData['year_of_birth']}</span>
              </li>
              <li>
                <span className={styles['label']}>Gender:</span>
                <span className={styles['value']}>{genderDict[this.state.userData['gender']]}</span>
              </li>
              <li>
                <span className={styles['label']}>Date joined:</span>
                <span className={styles['value']}>{dateJoined.toUTCString()}</span>
              </li>
              <li>
                <span className={styles['label']}>Is active:</span>
                <span className={styles['value']}>{this.state.userData['is_active'] ? 'Active user' : 'User inactive'}</span>
              </li>
              <li>
                <span className={styles['label']}>Courses enrolled:</span>
                <span className={styles['value']}>{this.state.userData['courses'] ? this.state.userData['courses'].length : ""}</span>
              </li>
              <li>
                <span className={styles['label']}>Country:</span>
                <span className={styles['value']}>{this.state.userData['country'] ? countries.getName(this.state.userData['country'], "en") : "Not Available"}</span>
              </li>
              <li>
                <span className={styles['label']}>Level of education:</span>
                <span className={styles['value']}>{this.state.userData['level_of_education'] ? educationLevelsDict[this.state.userData['level_of_education']] : 'Not Available'}</span>
              </li>
              <li>
                <span className={styles['label']}>Email address:</span>
                <span className={styles['value']}><a href={"mailto:" + this.state.userData['email']}>{this.state.userData['email']}</a></span>
              </li>
            </ul>
          </div>
          <UserCoursesList
            enrolledCoursesData={this.state.userData['courses'] ? this.state.userData['courses'] : []}
          />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({

})

const mapDispatchToProps = dispatch => ({
  addActiveApiFetch: () => dispatch(addActiveApiFetch()),
  removeActiveApiFetch: () => dispatch(removeActiveApiFetch()),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SingleUserContent)
