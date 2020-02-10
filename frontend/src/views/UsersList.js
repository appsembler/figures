import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import apiConfig from 'base/apiConfig';
import { trackPromise } from 'react-promise-tracker';
import styles from './_users-list-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentStatic from 'base/components/header-views/header-content-static/HeaderContentStatic';
import Paginator from 'base/components/layout/Paginator';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck } from '@fortawesome/free-solid-svg-icons';

import classNames from 'classnames/bind';
let cx = classNames.bind(styles);


class UsersList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      usersList: [],
      perPage: 20,
      count: 0,
      pages: 0,
      currentPage: 1,
    };

    this.getUsers = this.getUsers.bind(this);
    this.setPerPage = this.setPerPage.bind(this);
  }

  getUsers(page = 1) {
    const offset = (page-1) * this.state.perPage;
    const requestUrl = apiConfig.learnersGeneral + '?limit=' + this.state.perPage + '&offset=' + offset;
    trackPromise(
      fetch((requestUrl), { credentials: "same-origin" })
        .then(response => response.json())
        .then(json => this.setState({
          usersList: json['results'],
          count: json['count'],
          pages: Math.ceil(json['count'] / this.state.perPage),
          currentPage: page,
        })
      )
    )
  }

  setCurrentPage(newValue) {
    this.setState({
      currentPage: newValue,
    })
  }

  setPerPage(newValue) {
    this.setState({
      perPage: newValue
    }, () => {
      this.getUsers();
    })
  }

  componentDidMount() {
    this.getUsers();
  }

  render() {

    const listItems = this.state.usersList.map((user, index) => {
      return (
        <li key={user['id']} className={styles['user-list-item']}>
          <div className={styles['user-fullname']}>
            <Link
              className={styles['user-fullname-link']}
              to={'/figures/user/' + user['id']}
            >
              {user['fullname']}
            </Link>
          </div>
          <div className={styles['username']}>
            {user['username']}
          </div>
          <div className={styles['is-active']}>
            {user['is_active'] ? <FontAwesomeIcon icon={faCheck} className={styles['checkmark-icon']} /> : '-'}
          </div>
          <div className={styles['number-of-courses']}>
            {user['courses'].length}
          </div>
          <div className={styles['action-container']}>
            <Link
              className={styles['user-action']}
              to={'/figures/user/' + user['id']}
            >
              User details
            </Link>
          </div>
        </li>
      )
    })

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentStatic
            title='Users list'
            subtitle={'This view allows you to browse your sites users. Total number of users: ' + this.state.count + '.'}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'users-content': true})}>
          {this.state.pages ? (
            <Paginator
              pageSwitchFunction={this.getUsers}
              currentPage={this.state.currentPage}
              perPage={this.state.perPage}
              pages={this.state.pages}
              changePerPageFunction={this.setPerPage}
            />
          ) : ''}
          <ul className={styles['users-list']}>
            <li key='list-header' className={cx(styles['user-list-item'], styles['list-header'])}>
              <div className={styles['user-fullname']}>
                User full name:
              </div>
              <div className={styles['username']}>
                Username:
              </div>
              <div className={styles['is-active']}>
                Is user active:
              </div>
              <div className={styles['number-of-courses']}>
                Courses enroled in:
              </div>
              <div className={styles['action-container']}>

              </div>
            </li>
            {listItems}
          </ul>
          {this.state.pages ? (
            <Paginator
              pageSwitchFunction={this.getUsers}
              currentPage={this.state.currentPage}
              perPage={this.state.perPage}
              pages={this.state.pages}
              changePerPageFunction={this.setPerPage}
            />
          ) : ''}
        </div>
      </div>
    );
  }
}

export default UsersList
