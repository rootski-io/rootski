import { ThunkAction, ThunkDispatch } from "redux-thunk";
import { Action, AnyAction, Dispatch } from "redux";
import axios from "axios";
import {
  SearchUpdateTextAction,
  SEARCH_UPDATE_TEXT,
  SearchApiResponse,
} from "./types";
import { Word } from "../../models/models";
import { SearchUpdateRequestAction, SEARCH_UPDATE_REQUEST } from "./types";
import { RUSSIAN_API_URL } from "../../config/constants";
import {
  SearchWordsResultsAction,
  SEARCH_WORDS_RESULTS,
  SearchUpdateLoadingAction,
  SEARCH_UPDATE_LOADING,
  SearchUpdateUserTypingAction,
  SEARCH_UPDATE_USER_TYPING,
  SearchResultsAction,
} from "./types";

const searchWordsResults = function (
  matchedWords: Array<Word>
): SearchWordsResultsAction {
  return {
    type: SEARCH_WORDS_RESULTS,
    payload: matchedWords,
  };
};

/**
 * Call this action to cancel the last search request if there was one and make a new request
 * @param cancelToken cancel token used to cancel axios request
 */
export const updateSearchRequest = (
  cancelToken: ReturnType<typeof axios.CancelToken.source> | null
): SearchUpdateRequestAction => ({
  type: SEARCH_UPDATE_REQUEST,
  payload: cancelToken,
});

export const updateLoading = function (
  loading: boolean
): SearchUpdateLoadingAction {
  return {
    type: SEARCH_UPDATE_LOADING,
    payload: loading,
  };
};

// DELETE ???
export const updateUserTyping = function (
  userIsTyping: boolean
): SearchUpdateUserTypingAction {
  return {
    type: SEARCH_UPDATE_USER_TYPING,
    payload: userIsTyping,
  };
};

export const searchUpdateText = function (
  searchText: string
): SearchUpdateTextAction {
  return {
    type: SEARCH_UPDATE_TEXT,
    payload: searchText,
  };
};

export const searchAction = function (dispatch: Dispatch) {
  return (searchKey: string): void => {
    // clear current search results
    if (searchKey == "") {
      dispatch(searchWordsResults([]));
    }

    // search on truthy inputs
    if (searchKey != "") {
      // start loading
      dispatch(updateLoading(true));

      const searchUrl = `${RUSSIAN_API_URL}/search/`;

      // prepare to store request cancel token
      let cancelToken = axios.CancelToken.source();

      // dispatch latest cancel token (probably before the above lines finish)
      dispatch(updateSearchRequest(cancelToken));

      // perform GET /search request
      axios
        .get(`${searchUrl}${searchKey.toLowerCase()}`, {
          cancelToken: cancelToken.token,
        })
        .then((response: { data: SearchApiResponse }) => {
          // store search results in state
          dispatch(searchWordsResults(response.data.words));
        })
        .then(() => {
          dispatch(updateLoading(false));
        })
        .catch((err) => {
          // if error is because we cancelled request
          if (axios.isCancel(err)) {
            console.log(`Cancelled search request: "${searchKey}"`);
            return;
          }
          // otherwise we want to see it
          throw err;
        });
    }
  };
};
