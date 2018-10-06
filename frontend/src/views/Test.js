import React, { Component } from 'react';
import figuresLogo from 'base/images/logo/figures--logo--negative.svg';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import 'base/App.css';
import 'base/sass/base/_grid.scss';

class Test extends Component {
  render() {
    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout />
        <section className="ef--container ef--base-grid-layout">

        </section>
        <div className="App">
          <header className="App-header">
            <img src={figuresLogo} className="App-logo" alt="logo" />
            <h1 className="App-title">TEST JEBOTE</h1>
          </header>
          <p className="App-intro">
            To get started, edit <code>src/App.js</code> and save to reload.
          </p>
        </div>
      </div>
    );
  }
}

export default Test;
