import React from "react";
import { useParams } from "react-router-dom";
import { WordType } from "../../models/models";
import Typography from "@material-ui/core/Typography";
import WordPage from "../pages/word-page/WordPage";

// for fetching the word data on load
import { AppState } from "../../redux/reducers/index";
import { useSelector, shallowEqual, useDispatch } from "react-redux";
import { fetchWordDataAction } from "../../redux/actions/WordActions";

// see the WORD_PAGE_ROUTE in ./index.tsx
export interface WordPageRouteParams {
  word_type: WordType;
  word_id: string;
}

export const WordPageRouteHandler = () => {
  // get :word_id: and :word_type: from the url parameters
  // @ts-ignore
  const routeParams: WordPageRouteParams = useParams();
  const { word_type, word_id } = routeParams;
  const word_id_integer = parseInt(word_id);

  /**
   * Redux State
   */
  const selectReduxData = (state: AppState) => ({
    authToken: state.authData.idToken,
  });
  const reduxData: ReturnType<typeof selectReduxData> = useSelector(
    selectReduxData,
    shallowEqual
  );
  const userIsLoggedIn: boolean = reduxData.authToken !== null;
  const authToken: string | undefined =
    reduxData.authToken !== null ? reduxData.authToken : undefined;

  // redux actions
  const dispatch = useDispatch();
  const fetchWordData = fetchWordDataAction(dispatch); // creates a fetchWordData action function

  // fetch the wordData when the component is created
  fetchWordData(word_id_integer, word_type, authToken);

  return <WordPage />;
};
