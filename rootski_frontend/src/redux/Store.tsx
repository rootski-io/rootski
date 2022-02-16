import { createStore, applyMiddleware } from "redux";
import { composeWithDevTools } from "redux-devtools-extension"; // not sure about this
import thunk from "redux-thunk";
import { rootReducer } from "./reducers";

const initialState = {};

const middleware = [thunk];

const store = createStore(
  rootReducer,
  initialState,
  // NOTE, you don't have to call composeWithDevTools... not sure what that does
  composeWithDevTools(applyMiddleware(...middleware))
);

export default store;
