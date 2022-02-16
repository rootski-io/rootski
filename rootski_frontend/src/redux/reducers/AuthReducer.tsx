import {
  AuthAction,
  LOGIN_USER,
  LOGOUT_USER,
  CognitoTokenPayload,
  LoginUserAction,
  LogoutUserAction,
} from "../actions/types";

export interface AuthState {
  idToken: string | null;
  idTokenPayload: CognitoTokenPayload | null;
}

const initialState: AuthState = {
  idToken: null,
  idTokenPayload: null,
};

export function authReducer(
  state = initialState,
  action: AuthAction
): AuthState {
  let a: AuthAction;
  switch (action.type) {
    case LOGIN_USER:
      console.log("changing login state!", action);
      a = action as LoginUserAction;
      return {
        ...state,
        idToken: action.payload.idToken,
        idTokenPayload: action.payload.idTokenPayload,
      };
    case LOGOUT_USER:
      console.log("changing login state!", action);
      a = action as LogoutUserAction;
      return {
        ...state,
        idToken: action.payload.idToken,
        idTokenPayload: action.payload.idTokenPayload,
      };
    default:
      return state;
  }
}
