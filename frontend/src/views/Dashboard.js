import React, { Component } from 'react';
import logo from 'base/logo.svg';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/HeaderContentMaus';
import 'base/App.css';
import 'base/sass/base/_grid.scss';

class Dashboard extends Component {
  render() {
    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentMaus />
        </HeaderAreaLayout>
        <section className="ef--container ef--base-grid-layout">

        </section>
        <div className="App">
          <header className="App-header">
            <img src={logo} className="App-logo" alt="logo" />
            <h1 className="App-title">Welcome to React</h1>
          </header>
          <p className="App-intro">
            To get started, edit <code>src/App.js</code> and save to reload.
          </p>
        </div>
      </div>
    );
  }
}

export default Dashboard;
