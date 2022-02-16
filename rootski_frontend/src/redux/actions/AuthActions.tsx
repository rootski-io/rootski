import { CognitoIdToken } from "amazon-cognito-identity-js";
import {
  LoginUserAction,
  LogoutUserAction,
  LOGIN_USER,
  LOGOUT_USER,
  CognitoTokenPayload,
} from "./types";
import { Dispatch } from "redux";
import axios from "axios";

// populate the login state
const loginUser = (
  idToken: string,
  idTokenPayload: CognitoTokenPayload
): LoginUserAction => {
  return { type: LOGIN_USER, payload: { idToken, idTokenPayload } };
};

// wrap the loginUser action with a dispatcher so it can be manually dispatched from components
export const loginUserAction = (dispatch: Dispatch) => {
  return (idToken: string, idTokenPayload: CognitoTokenPayload) => {
    // configure axios to include this token in its headers in addition to updating the redux state
    // yep... axios is kind of a global variable, and this may be confusing if you don't know this is
    // here. Notes in the api/*.tsx files will point to this behavior
    axios.defaults.headers.common["Authorization"] = `Bearer ${idToken}`;
    dispatch(loginUser(idToken, idTokenPayload));
  };
};

// clear the login state
const logoutUser = (): LogoutUserAction => {
  return {
    type: LOGOUT_USER,
    payload: { idToken: null, idTokenPayload: null },
  };
};

// wrap the loginUser action with a dispatcher so it can be manually dispatched from components
export const logoutUserAction = (dispatch: Dispatch) => {
  return () => dispatch(logoutUser());
};
