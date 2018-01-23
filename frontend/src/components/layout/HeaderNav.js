import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import 'base/sass/layouts/_header-nav.scss';

class HeaderNav extends Component {
  render() {
    return (
      <div className="ef--header-nav">
        <NavLink
          to="#"
          className="ef--header-nav__link"
        >
          Dashboard
        </NavLink>
        <NavLink
          to="#"
          className="ef--header-nav__link"
        >
          Reports
        </NavLink>
      </div>
    );
  }
}

export default HeaderNav;
