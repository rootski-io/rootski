import { combineReducers } from "redux";
import { searchReducer } from "./SearchReducer";
import { wordDataReducer } from "./WordReducer";
import { authReducer } from "./AuthReducer";

// @ts-ignore
export const rootReducer = combineReducers({
  search: searchReducer,
  wordData: wordDataReducer,
  authData: authReducer,
});

export type AppState = ReturnType<typeof rootReducer>;
