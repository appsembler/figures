import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import classNames from 'classnames/bind';
import { connect } from 'react-redux';
import Immutable from 'immutable';
import styles from './_dashboard-content.scss';
import HeaderAreaLayout from 'base/components/layout/HeaderAreaLayout';
import HeaderContentMaus from 'base/components/header-views/header-content-maus/HeaderContentMaus';
import BaseStatCard from 'base/components/stat-cards/BaseStatCard';

let cx = classNames.bind(styles);


class DashboardContent extends Component {

  constructor(props) {
    super(props);
    this.state = {

    };
  }

  render() {

    return (
      <div className="ef--layout-root">
        <HeaderAreaLayout>
          <HeaderContentMaus
            showHistoryButton
          />
        </HeaderAreaLayout>
        <div className={cx({ 'container': true, 'base-grid-layout': true, 'dashboard-content': true})}>
          <BaseStatCard
            mainValue={this.props.generalData.getIn(['registeredUsers', 'current_month'], 0)}
            valueHistory={this.props.generalData.getIn(['registeredUsers', 'history'], [])}
            cardTitle='Utilisateurs enregistrés'
          />
          <BaseStatCard
            mainValue={this.props.generalData.getIn(['newUsers', 'current_month'], 0)}
            valueHistory={this.props.generalData.getIn(['newUsers', 'history'], [])}
            cardTitle='Nouveaux utilisateurs'
          />
          <BaseStatCard
            mainValue={this.props.generalData.getIn(['courseEnrollments', 'current_month'], 0)}
            valueHistory={this.props.generalData.getIn(['courseEnrollments', 'history'], [])}
            cardTitle='Enregistrement aux cours'
          />
          <BaseStatCard
            mainValue={this.props.generalData.getIn(['courseCompletions', 'current_month'], 0)}
            valueHistory={this.props.generalData.getIn(['courseCompletions', 'history'], [])}
            cardTitle='Achèvemennt des cours'
          />
        </div>
        <div className={cx({ 'container': true, 'functionality-callout': true})}>
          <h3>Accedez rapidement à un cours en utilisant <strong>"Recherche cours"</strong> sur le menu en haut, ou <strong>Parcourir tous les cours</strong> ci dessous:</h3>
          <NavLink
            to="/figures/courses"
            className={styles['functionality-callout-cta']}
          >
            Parcourir tous les cours
          </NavLink>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  generalData: Immutable.fromJS(state.generalData),
})

export default connect(
  mapStateToProps,
)(DashboardContent)
