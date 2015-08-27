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
      currentPage: -1,
      colunms: [],
      top: null
    }
  },
  getDefaultProps: function(){
    return {
      t: null,
      store: null,
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
    if (this.state.top != null) {
      if (this.state.currentPage != -1 && this.state.top[this.state.currentPage] != null) {
        var rows = this.state.top[this.state.currentPage].map(function(data, index){
              return (
                <tr>
                  <td>{index}</td>
                  <td>{data.stock.symbol}</td>
                  //<td>{data.price}</td>
                  <td>{data.epsQuarterGrowth}</td>
                  <td>{data.epsAnnualGrowth}</td>
                  <td>{data.nextYearPE}</td>
                  <td>{data.rate}</td>
                </tr>
                );
          }.bind(this)); 
        console.log(rows);
      }
    }
    return (
      <Table responsive>
        <thead>
          <tr>
            {col}
          </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
      </Table>
    );
  }
});

module.exports = RankList;

