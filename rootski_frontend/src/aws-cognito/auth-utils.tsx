/**
 * There should be an AWS Cognito User Pool with Google set up as an OAuth
 * Identity Provider. There is a CDK project to create that in `infrastructure/`
 *
 * The body of this config file comes from this documentation page:
 * https://docs.amplify.aws/lib/auth/start/q/platform/js#re-use-existing-authentication-resource
 *
 *
 */
import { CognitoUser, CognitoIdToken } from "amazon-cognito-identity-js";
import Amplify, { Auth } from "aws-amplify";

// Cognito stack variables. Get these from the Cognito stack outputs!
const COGNITO_USER_POOL_REGION =
  process.env.REACT_APP__COGNITO_USER_POOL_REGION || "us-west-2";
const COGNITO_USER_POOL_ID =
  process.env.REACT_APP__COGNITO_USER_POOL_ID || "us-west-2_NMATFlcVJ";
const USER_POOL_WEB_CLIENT_ID =
  process.env.REACT_APP__USER_POOL_WEB_CLIENT_ID ||
  "35ufe1nk2tasug2gmbl5l9mra3";
const REDIRECT_SIGN_IN_URLS =
  process.env.REACT_APP__REDIRECT_SIGN_IN_URLS ||
  "https://www.rootski.io,http://localhost:3000"; // this can be a comma separated string
const REDIRECT_SIGN_OUT_URLS =
  process.env.REACT_APP__REDIRECT_SIGN_OUT_URLS ||
  "https://www.rootski.io,http://localhost:3000"; // this can be a comma separated string
const COGNITO_HOSTED_UI_FQDN =
  process.env.REACT_APP__COGNITO_HOSTED_UI_FQDN ||
  "rootski.auth.us-west-2.amazoncognito.com";
const COGNITO_WEB_CLIENT_ALLOWED_SCOPES =
  process.env.REACT_APP__COGNITO_WEB_CLIENT_ALLOWED_SCOPES ||
  "email,aws.cognito.signin.user.admin,openid,profile";

// get the localhost and rootski.io urls from REDIRECT_SIGN_IN_URLS and REDIRECT_SIGN_OUT_URLS
const [ROOTSKI_SIGN_IN_REDIRECT_URL, LOCALHOST_SIGN_IN_REDIRECT_URL] =
  REDIRECT_SIGN_IN_URLS.split(",");
const [ROOTSKI_SIGN_OUT_REDIRECT_URL, LOCALHOST_SIGN_OUT_REDIRECT_URL] =
  REDIRECT_SIGN_OUT_URLS.split(",");

// whether user is viewing from localhost (if not, it's probably rootski.io)
const isLocalhost = Boolean(
  window.location.hostname === "localhost" ||
    // [::1] is the IPv6 localhost address.
    window.location.hostname === "[::1]" ||
    // 127.0.0.1/8 is considered localhost for IPv4.
    window.location.hostname.match(
      /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
    )
);

let amplifyConfig = {
  Auth: {
    region: COGNITO_USER_POOL_REGION,
    userPoolId: COGNITO_USER_POOL_ID,
    userPoolWebClientId: USER_POOL_WEB_CLIENT_ID,
    // OPTIONAL - Hosted UI configuration
    oauth: {
      domain: COGNITO_HOSTED_UI_FQDN,
      scope: COGNITO_WEB_CLIENT_ALLOWED_SCOPES.split(","),
      redirectSignIn: ROOTSKI_SIGN_IN_REDIRECT_URL,
      redirectSignOut: ROOTSKI_SIGN_OUT_REDIRECT_URL,
      responseType: "code", // or "token", note that REFRESH token will only be generated when the responseType is code
    },
    // federationTarget: "COGNITO_USER_POOLS"
  },
};

// point auth redirects to localhost during local testing
const updatedAmplifyConfig = isLocalhost
  ? {
      // @ts-ignore
      ...amplifyConfig,
      // @ts-ignore
      oauth: {
        domain: COGNITO_HOSTED_UI_FQDN,
        scope: COGNITO_WEB_CLIENT_ALLOWED_SCOPES.split(","),
        redirectSignIn: LOCALHOST_SIGN_IN_REDIRECT_URL,
        redirectSignOut: LOCALHOST_SIGN_OUT_REDIRECT_URL,
        responseType: "code",
      },
    }
  : amplifyConfig;

Amplify.configure(updatedAmplifyConfig);

export const signOut = () => {
  Auth.signOut();

  // reload the page
  window.location.reload();
};

// this redirects the user to a "hosted ui" where they can choose between
// cognito, Google, and any other OAuth identity providers that are set up
export const signInWithCognito = () => {
  Auth.federatedSignIn();
};

export const signInWithFacebook = () => {
  // @ts-ignore
  Auth.federatedSignIn({
    provider: "Facebook",
  });
};

export const signInWithGoogle = () => {
  // @ts-ignore
  Auth.federatedSignIn({
    provider: "Google",
  });
};

/**
 * Fetch the current user's Cognito ID Token from the browser.
 */
export const getUserIdToken = async (): Promise<CognitoIdToken> => {
  const userInfo: CognitoUser = await Auth.currentAuthenticatedUser();
  const userSession = userInfo.getSignInUserSession();
  const idToken: CognitoIdToken | undefined = await userSession?.getIdToken();
  if (idToken === undefined) {
    throw Error("Failed to fetch userIdToken. Is the user logged in?");
  }
  return idToken;
};

export const logAuthData = async () => {
  try {
    const userIdToken = getUserIdToken();
    console.log("current user id token", userIdToken);
  } catch (e) {
    console.log(e);
  }

  try {
    const user = await Auth.currentAuthenticatedUser();
    console.log("current user", user);
  } catch (e) {
    console.log(e);
  }

  try {
    const credentials = await Auth.currentCredentials();
    console.log("current credentials", credentials);
  } catch (e) {
    console.log(e);
  }

  try {
    const userCredentials = await Auth.currentUserCredentials();
    console.log("current user credentials", userCredentials);
  } catch (e) {
    console.log(e);
  }

  try {
    const userInfo = await Auth.currentUserInfo();
    console.log("current user info", userInfo);
  } catch (e) {
    console.log(e);
  }

  try {
    const poolUser = await Auth.currentUserPoolUser();
    console.log("current pool user", poolUser);
  } catch (e) {
    console.log(e);
  }
};
