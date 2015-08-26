var React = require('react');

var Router = require('react-router')
  , RouteHandler = Router.RouteHandler
  , Route = Router.Route;

var ReactBootstrap = require('react-bootstrap')
  , Nav = ReactBootstrap.Nav
  , Navbar = ReactBootstrap.Navbar
  , NavItem = ReactBootstrap.NavItem
  , ButtonToolbar = ReactBootstrap.ButtonToolbar
  , Button = ReactBootstrap.Button
  , DropdownButton = ReactBootstrap.DropdownButton
  , MenuItem = ReactBootstrap.MenuItem
  , Jumbotron = ReactBootstrap.Jumbotron
  , Row = ReactBootstrap.Row
  , Col = ReactBootstrap.Col
  , Grid = ReactBootstrap.Grid
  , Table = ReactBootstrap.Table
  , Panel = ReactBootstrap.Panel
  , TabbedArea = ReactBootstrap.TabbedArea
  , TabPane = ReactBootstrap.TabPane
  ;

var ReactRouterBootstrap = require('react-router-bootstrap');

var RankList = React.createClass({
  getInitialState: function(){
    return {
      selectedRow: -1,
      colunms: []
    }
  },
  getDefaultProps: function(){
    return {
      t: null,
      store: null
    }
  },
  componentDidMount: function() {
    if (this.props.store != null) {
      this.props.store.addChangeListener(this._onChange);
    }
  },
  componentWillUnmount: function() {
    if (this.props.store != null) {
      this.props.store.removeChangeListener(this._onChange);
    }
  },
  _onChange: function() {
    if (this.props.store != null) {
      this.setState(this.props.store.getState());
    }
  },
  render: function() {
    var col = this.state.colunms.map(function(column){
            return <th>{this.props.t(column)}</th>;
          }.bind(this)); 
    return (
      <Table responsive>
        <thead>
          <tr>
            {col}
          </tr>
        </thead>
      </Table>
    );
  }
});

module.exports = RankList;

