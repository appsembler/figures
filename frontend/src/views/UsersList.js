import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import apiConfig from 'base/apiConfig';
import { trackPromise } from 'react-promise-tracker';
import styles from './_users-list-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentStatic from 'base/components/header-views/header-content-static/HeaderContentStatic';
import Paginator from 'base/components/layout/Paginator';
import ListSearch from 'base/components/inputs/ListSearch';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck, faAngleDoubleUp, faAngleDoubleDown } from '@fortawesome/free-solid-svg-icons';

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
      searchQuery: '',
      ordering: 'profile__name',
    };

    this.getUsers = this.getUsers.bind(this);
    this.setPerPage = this.setPerPage.bind(this);
    this.setSearchQuery = this.setSearchQuery.bind(this);
    this.setOrdering = this.setOrdering.bind(this);
    this.constructApiUrl = this.constructApiUrl.bind(this);
  }

  constructApiUrl(rootUrl, searchQuery, orderingType, perPageLimit, resultsOffset) {
    let requestUrl = rootUrl;
    // add search term
    requestUrl += '?search=' + searchQuery;
    // add ordering
    requestUrl += '&ordering=' + orderingType;
    // add results per page limit
    requestUrl += '&limit=' + perPageLimit;
    // add results offset
    requestUrl += '&offset=' + resultsOffset;
    // return
    return requestUrl;
  }

  getUsers(page = 1) {
    const offset = (page-1) * this.state.perPage;
    const requestUrl = this.constructApiUrl(apiConfig.learnersGeneral, this.state.searchQuery, this.state.ordering, this.state.perPage, offset);
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

  setPerPage(newValue) {
    this.setState({
      perPage: newValue,
    }, () => {
      this.getUsers();
    })
  }

  setSearchQuery(newValue) {
    this.setState({
      searchQuery: newValue
    }, () => {
      this.getUsers();
    })
  }

  setOrdering(newValue) {
    this.setState({
      ordering: newValue
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
            <div className={styles['in-cell-label-value']}>
              <div className={styles['mobile-label']}>
                Full name:
              </div>
              <div className={styles['mobile-value']}>
                <Link
                  className={styles['user-fullname-link']}
                  to={'/figures/user/' + user['id']}
                >
                  {user['fullname']}
                </Link>
              </div>
            </div>
          </div>
          <div className={styles['username']}>
            <div className={styles['in-cell-label-value']}>
              <div className={styles['mobile-label']}>
                Username:
              </div>
              <div className={styles['mobile-value']}>
                {user['username']}
              </div>
            </div>
          </div>
          <div className={styles['is-active']}>
            <div className={styles['in-cell-label-value']}>
              <div className={styles['mobile-label']}>
                Is activated:
              </div>
              <div className={styles['mobile-value']}>
                {user['is_active'] ? <FontAwesomeIcon icon={faCheck} className={styles['checkmark-icon']} /> : '-'}
              </div>
            </div>
          </div>
          <div className={styles['date-joined']}>
            <div className={styles['in-cell-label-value']}>
              <div className={styles['mobile-label']}>
                Date joined:
              </div>
              <div className={styles['mobile-value']}>
                {user['date_joined']}
              </div>
            </div>
          </div>
          <div className={styles['number-of-courses']}>
            <div className={styles['in-cell-label-value']}>
              <div className={styles['mobile-label']}>
                No. of courses:
              </div>
              <div className={styles['mobile-value']}>
                {user['courses'].length}
              </div>
            </div>
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
            subtitle={'This view allows you to browse your sites users. Total number of results: ' + this.state.count + '.'}
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'users-content': true})}>
          <ListSearch
            valueChangeFunction={this.setSearchQuery}
            inputPlaceholder='Search by users name, username or email...'
          />
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
                <button
                  className={styles['sorting-header-button']}
                  onClick={() => (this.state.ordering !== 'profile__name') ? this.setOrdering('profile__name') : this.setOrdering('-profile__name')}
                >
                  <span>
                    User full name
                  </span>
                  {(this.state.ordering === 'profile__name') ? (
                    <FontAwesomeIcon icon={faAngleDoubleUp} />
                  ) : (this.state.ordering === '-profile__name') ? (
                    <FontAwesomeIcon icon={faAngleDoubleDown} />
                  ) : ''}
                </button>
              </div>
              <div className={styles['username']}>
                <button
                  className={styles['sorting-header-button']}
                  onClick={() => (this.state.ordering !== 'username') ? this.setOrdering('username') : this.setOrdering('-username')}
                >
                  <span>
                    Username
                  </span>
                  {(this.state.ordering === 'username') ? (
                    <FontAwesomeIcon icon={faAngleDoubleUp} />
                  ) : (this.state.ordering === '-username') ? (
                    <FontAwesomeIcon icon={faAngleDoubleDown} />
                  ) : ''}
                </button>
              </div>
              <div className={styles['is-active']}>
                <button
                  className={styles['sorting-header-button']}
                  onClick={() => (this.state.ordering !== 'is_active') ? this.setOrdering('is_active') : this.setOrdering('-is_active')}
                >
                  <span>
                    Is activated
                  </span>
                  {(this.state.ordering === 'is_active') ? (
                    <FontAwesomeIcon icon={faAngleDoubleUp} />
                  ) : (this.state.ordering === '-is_active') ? (
                    <FontAwesomeIcon icon={faAngleDoubleDown} />
                  ) : ''}
                </button>
              </div>
              <div className={styles['date-joined']}>
                <button
                  className={styles['sorting-header-button']}
                  onClick={() => (this.state.ordering !== 'date_joined') ? this.setOrdering('date_joined') : this.setOrdering('-date_joined')}
                >
                  <span>
                    Date joined
                  </span>
                  {(this.state.ordering === 'date_joined') ? (
                    <FontAwesomeIcon icon={faAngleDoubleUp} />
                  ) : (this.state.ordering === '-date_joined') ? (
                    <FontAwesomeIcon icon={faAngleDoubleDown} />
                  ) : ''}
                </button>
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
