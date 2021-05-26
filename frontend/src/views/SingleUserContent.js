import React, { Component } from 'react';
import Immutable from 'immutable';
import { connect } from 'react-redux';
import { trackPromise } from 'react-promise-tracker';
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
  "m": "Homme",
  "f": "Femme",
  "o": "Autre / non precisé"
}

let cx = classNames.bind(styles);

class SingleUserContent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      userData: Immutable.Map()
    };

    this.fetchUserData = this.fetchUserData.bind(this);
  }

  fetchUserData = () => {
    trackPromise(
      fetch((apiConfig.learnersDetailed + this.props.userId + '/'), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          userData: Immutable.fromJS(json)
        }))
    )
  }

  componentDidMount() {
    this.fetchUserData();
  }

  render() {
    const dateJoined = new Date(this.state.userData.getIn(['date_joined']));

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentUser
            image = {this.state.userData.getIn(['profile_image', 'image_url_large'])}
            name = {this.state.userData.getIn(['name'])}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'user-content': true})}>
          <div className={styles['user-information']}>
            <div className={styles['name']}>
              {this.state.userData['name']}
            </div>
            <ul className={styles['user-details']}>
              <li>
                <span className={styles['label']}>Nom d'utilisateur:</span>
                <span className={styles['value']}>{this.state.userData.getIn(['username'])}</span>
              </li>
              <li>
                <span className={styles['label']}>Date de naissance:</span>
                <span className={styles['value']}>{this.state.userData.getIn(['year_of_birth'])}</span>
              </li>
              <li>
                <span className={styles['label']}>Genre:</span>
                <span className={styles['value']}>{genderDict[this.state.userData.getIn(['gender'])]}</span>
              </li>
              <li>
                <span className={styles['label']}>Date d'inscription:</span>
                <span className={styles['value']}>{dateJoined.toUTCString()}</span>
              </li>
              <li>
                <span className={styles['label']}>Compte activé:</span>
                <span className={styles['value']}>{this.state.userData.getIn(['is_active'], false) ? 'Actif' : 'Inactif'}</span>
              </li>
              <li>
                <span className={styles['label']}>Cours suivis:</span>
                <span className={styles['value']}>{this.state.userData.getIn(['courses']) ? this.state.userData.getIn(['courses']).length : ""}</span>
              </li>
              <li>
                <span className={styles['label']}>Pays:</span>
                <span className={styles['value']}>{this.state.userData.getIn(['country']) ? countries.getName(this.state.userData.getIn(['country']), "en") : "Not Available"}</span>
              </li>
              <li>
                <span className={styles['label']}>Niveau d'éducation:</span>
                <span className={styles['value']}>{this.state.userData.getIn(['level_of_education']) ? educationLevelsDict[this.state.userData.getIn(['level_of_education'])] : 'Not Available'}</span>
              </li>
              <li>
                <span className={styles['label']}>Email:</span>
                <span className={styles['value']}><a href={"mailto:" + this.state.userData.getIn(['email'])}>{this.state.userData.getIn(['email'])}</a></span>
              </li>
            </ul>
          </div>
          <UserCoursesList
            enrolledCoursesData={this.state.userData.getIn(['courses'], [])}
          />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({

})

const mapDispatchToProps = dispatch => ({

})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SingleUserContent)
