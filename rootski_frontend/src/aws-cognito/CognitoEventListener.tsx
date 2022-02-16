/**
 * This component is a bridge between AWS Cognito auth events
 * and the redux state.
 *
 * When auth events such as sign in, sign up, and sign out take place,
 * a react action is dispatched, updating the latest user information
 * into the Auth reducer.
 *
 * We needed to use a component for this, because only components can
 * use the react hooks for sending state to redux (e.g. use the dispatch method).
 *
 * The inspiration for this component comes from the amplify docs here:
 * https://docs.amplify.aws/lib/auth/auth-events/q/platform/js
 */

import { Hub } from "aws-amplify";
import { useDispatch } from "react-redux";
import {
  loginUserAction,
  logoutUserAction,
} from "../redux/actions/AuthActions";
import { getUserIdToken } from "./auth-utils";
import { CognitoIdToken } from "amazon-cognito-identity-js";
import { CognitoTokenPayload } from "../redux/actions/types";

export const CognitoEventListener = () => {
  // redux actions
  const dispatch = useDispatch();
  const loginUser = loginUserAction(dispatch); // creates a loginUser action function
  const logoutUser = logoutUserAction(dispatch); // creates a logoutUser action function

  const updateUserCredentials = async () => {
    const cognitoIdToken: CognitoIdToken = await getUserIdToken();
    const idToken: string = cognitoIdToken.getJwtToken();
    // @ts-ignore
    const idTokenPayload: CognitoTokenPayload = cognitoIdToken.decodePayload();
    loginUser(idToken, idTokenPayload);
  };

  // logoutUser();
  updateUserCredentials();

  const listener = async (data: any) => {
    switch (data.payload.event) {
      case "signIn":
        console.log("user signed in");
        updateUserCredentials();
        break;
      case "signUp":
        console.log("user signed up");
        updateUserCredentials();
        break;
      case "signOut":
        console.log("user signed out");
        logoutUser();
        break;
      case "signIn_failure":
        console.log("user sign in failed");
        logoutUser();
        break;
      case "tokenRefresh":
        console.log("token refresh succeeded");
        break;
      case "tokenRefresh_failure":
        console.log("token refresh failed");
        logoutUser();
        break;
      case "configured":
        console.log("the Auth module is configured");
    }
  };

  Hub.listen("auth", listener);

  return null;
};
