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
    ;

var ReactRouterBootstrap = require('react-router-bootstrap')
//    , NavItem = ReactRouterBootstrap.NavItem
//    , DropdownButton = ReactRouterBootstrap.DropdownButton
//    , NavItemLink = ReactRouterBootstrap.NavItemLink
//    , MenuItem = ReactRouterBootstrap.MenuItem
    , MenuItemLink = ReactRouterBootstrap.MenuItemLink
    , ButtonLink = ReactRouterBootstrap.ButtonLink
    ;

var AppStore = require('./stores/AppStore');
var UpdateActions = require('./actions/UpdateActions');

var supportedLang = ["en-US", "zh-CN"];

initLang = navigator.language || navigator.userLanguage;

if ($.inArray(initLang, supportedLang) == -1) {
    initLang = "en-US";
}

i18n.init({lng: initLang, getAsync: false});

var App = React.createClass({
    // Invoked once after the first render
    getInitialState: function(){
        return {
          t: i18n.t
        }
    },
    handleChangeLanguage: function(selectedKey) {
        var lang = selectedKey;
        UpdateActions.updateLanguage(lang);
    },
    componentDidMount: function() {
        AppStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        AppStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {this.setState(AppStore.getState());},
    render: function () {
        return (
            <div>
                <Navbar brand={this.state.t('app.name')}>
                    <Nav>
                        <NavItem eventKey={1} href="#">{this.state.t('nav.home')}</NavItem>
                        <NavItem eventKey={2} href="#">{this.state.t('nav.rank')}</NavItem>
                        <DropdownButton eventKey={3} title={this.state.t('nav.tools')}>
                            <MenuItem eventKey="1">Action</MenuItem>
                            <MenuItem eventKey="2">Another action</MenuItem> 
                            <MenuItem eventKey="3">Something else here</MenuItem>
                            <MenuItem divider />
                            <MenuItem eventKey="4">Separated link</MenuItem>
                        </DropdownButton>
                    </Nav>
                    <Nav right> 
                        <DropdownButton eventKey={5} onSelect={this.handleChangeLanguage} title={this.state.t('nav.lang')}>
                            <MenuItem eventKey="en-US">{this.state.t('nav.lang-en-US')}</MenuItem>
                            <MenuItem eventKey="zh-CN">{this.state.t('nav.lang-zh-CN')}</MenuItem> 
                        </DropdownButton>
                    </Nav>
                </Navbar>

                <Grid>
                    <Row>
                        <Col xs={12} md={8}>
                            <Jumbotron>
                                <h1>Hello, world!</h1>
                                <p>This is a simple hero unit, a simple jumbotron-style component for
                                calling extra attention to featured content or information.</p>
                                <p>
                                    <Button bsStyle="primary">Learn more</Button>
                                </p>
                            </Jumbotron>

                            <ButtonToolbar>
                                <Button>Default</Button>
                                <Button bsStyle="primary">Primary</Button>
                                <Button bsStyle="success">Success</Button>
                                <Button bsStyle="info">Info</Button>
                                <Button bsStyle="warning">Warning</Button>
                                <Button bsStyle="danger">Danger</Button>
                                <Button bsStyle="link">Link</Button>
                            </ButtonToolbar>

                            <RouteHandler/>
                        </Col>
                    </Row>
                </Grid>

            </div>
        );
    }
});

var routes = (
    <Route handler={App} path="/">
        
    </Route>
);

Router.run(routes, function (Handler) {
    React.render(<Handler/>, document.body);
});