// @ts-nocheck
import React from "react";
import {
  fade,
  makeStyles,
  Theme,
  createStyles,
  withStyles,
} from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import HomeIcon from "@material-ui/icons/Home";
import PersonIcon from "@material-ui/icons/Person";
import NoteIcon from "@material-ui/icons/Note";
import SearchBar from "./SearchBar";
import { Tabs, Tab, useMediaQuery, Button } from "@material-ui/core";
import { theme } from "../theme";
import EmojiPeopleRoundedIcon from "@material-ui/icons/EmojiPeopleRounded";
import InputRoundedIcon from "@material-ui/icons/InputRounded";
import IconButton from "@material-ui/core/IconButton";
import { AppState } from "../redux/reducers/index";
import { shallowEqual, useSelector } from "react-redux";
import { signInWithCognito, signOut } from "../../aws-cognito/auth-utils";

import { ReactComponent as RootskiLogoWhiteBoldSVG } from "../../assets/images/rootski-logo-white.svg";
import { useHistory } from "react-router";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    toolbarMargin: { ...theme.mixins.toolbar }, // push content out from under the AppBar
    tabs: {},
    tab: {
      maxWidth: "5px",
    },
    rootskiLogo: {
      width: "100px",
      marginRight: "20px",
      marginLeft: "10px",
    },
    grow: {
      flexGrow: 1,
    },
    title: {
      display: "none",
      [theme.breakpoints.up("sm")]: {
        display: "block",
        marginRight: "15px",
      },
    },
    sectionDesktop: {
      display: "none",
      [theme.breakpoints.up("md")]: {
        display: "flex",
      },
    },
  })
);

// white button component for top bar
const WhiteButton = withStyles((theme: Theme) => ({
  root: {
    border: "none",
    marginLeft: "8px",
    color: "#fff",
    fontSize: "16px",
  },
}))(Button);

export const Header = () => {
  // style
  const classes = useStyles();
  const smallScreen = useMediaQuery(theme.breakpoints.down("sm"));
  const browserHistory = useHistory();

  const navigateHome = () => {
    browserHistory.push("/");
  };

  // redux state
  const selectReduxData = (state: AppState) => ({
    userIsLoggedIn: state.authData.idToken !== null,
  });
  const reduxData = useSelector(selectReduxData, shallowEqual);

  // Tabs
  const handleTabsChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setTabsValue(newValue);
  };
  const [tabsValue, setTabsValue] = React.useState(0);
  const renderTabs = (
    <Tabs
      className={classes.tabs}
      value={tabsValue}
      onChange={handleTabsChange}
    >
      <Tab label="Home" icon={<HomeIcon />} className={classes.tab} />
      <Tab label="My Study Sets" icon={<NoteIcon />} className={classes.tab} />
      <Tab label="Profile" icon={<PersonIcon />} className={classes.tab} />
    </Tabs>
  );

  const renderLoginButtons = () => {
    return (
      <>
        <WhiteButton
          onClick={signInWithCognito}
          variant="outlined"
          endIcon={<EmojiPeopleRoundedIcon />}
        >
          Sign In / Sign Up
        </WhiteButton>
        {/* <WhiteButton onClick={signInWithCognito} variant="outlined" endIcon={<InputRoundedIcon />}>Sign In</WhiteButton>
      <WhiteButton onClick={sign} variant="outlined" endIcon={<EmojiPeopleRoundedIcon />}>Register</WhiteButton> */}
      </>
    );
  };

  const renderLogoutButton = () => (
    <WhiteButton onClick={signOut} endIcon={<InputRoundedIcon />}>
      Sign Out
    </WhiteButton>
  );

  const renderLoginLogoutButtons = () => {
    if (reduxData.userIsLoggedIn) {
      return renderLogoutButton();
    } else {
      return renderLoginButtons();
    }
  };

  return (
    <div className={classes.grow}>
      <AppBar position="sticky">
        <Toolbar disableGutters={smallScreen}>
          <RootskiLogoWhiteBoldSVG
            className={classes.rootskiLogo}
            style={{ cursor: "pointer" }}
            onClick={() => {
              navigateHome();
            }}
          />

          {smallScreen ? null : <SearchBar />}
          <div className={classes.grow} />
          {/* {smallScreen ? null : renderTabs} */}
          {smallScreen ? null : renderLoginLogoutButtons()}
        </Toolbar>
      </AppBar>
    </div>
  );
};
