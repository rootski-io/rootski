// @ts-nocheck
import React from "react";
// import LoginForm from "./components/LoginForm"; // TODO: this component is for AWS amplify
// I will need to set this up from scratch later on, but for the time being,
// it is cluttering up the code
import { Provider } from "react-redux";
import store from "./redux/Store";
import SearchBar from "./components/page-layout/SearchBar";
import { Header } from "./components/page-layout/Header";
import {
  ThemeProvider,
  useMediaQuery,
  Container,
  Button,
} from "@material-ui/core";
import { theme } from "./components/theme";
import Footer from "./components/page-layout/Footer";
import Breakdown from "./components/Breakdown";
import WordPage from "./components/pages/word-page/WordPage";
import { HashRouter as Router, Route, Link, Switch } from "react-router-dom";
import { WORD_PAGE_ROUTE } from "./components/routing/index";
import { WordPageRouteHandler } from "./components/routing/WordPageRouteHandler";
import { useParams } from "react-router-dom";
import {
  signInWithCognito,
  signInWithGoogle,
  logAuthData,
} from "./aws-cognito/auth-utils";
import { CognitoEventListener } from "./aws-cognito/CognitoEventListener";
import { LandingPage } from "./components/pages/landing-page/LandingPage";

const SHOW_DEBUG_AUTH_BUTTONS = false;

export const App = () => {
  // const showFooter = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <ThemeProvider theme={theme} className="container">
      <Provider store={store}>
        <CognitoEventListener />
        <Router>
          <Header />
          {/* <LoginForm /> */}
          <Switch>
            <Route path={WORD_PAGE_ROUTE} children={<WordPageRouteHandler />} />
            <Route path={"/"} children={<LandingPage />} />
          </Switch>
        </Router>
        {SHOW_DEBUG_AUTH_BUTTONS ? <AuthButtons /> : null}
        {/* {showFooter ? <Footer /> : null} */}
      </Provider>
    </ThemeProvider>
  );
};

export default App;

/**
 * This is a utility component for debugging/testing auth.
 */
const AuthButtons = () => {
  return (
    <>
      <Button variant="contained" color="primary" onClick={signInWithCognito}>
        Login with Cognito
      </Button>
      <Button variant="contained" color="primary" onClick={signInWithGoogle}>
        Login with Google
      </Button>
      <Button variant="outlined" color="secondary" onClick={logAuthData}>
        Log Auth Data
      </Button>
    </>
  );
};
