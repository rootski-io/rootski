import { Word } from "../../models/models";
import axios from "axios";
import {
  SearchUpdateLoadingAction,
  SearchUpdateRequestAction,
  SearchUpdateTextAction,
  SearchUpdateUserTypingAction,
  SearchWordsAction,
  SearchWordsResultsAction,
  SEARCH_UPDATE_REQUEST,
} from "../actions/types";
import {
  SearchResultsAction,
  SEARCH_WORDS_RESULTS,
  SEARCH_UPDATE_TEXT,
  SEARCH_UPDATE_LOADING,
} from "../actions/types";

export interface SearchState {
  searchText: string;
  loading: boolean;
  matchedWords: Array<Word>;
  lastSearchRequest: ReturnType<typeof axios.CancelToken.source> | null;
  lastSearchRequestCancelled: boolean;
}

const initialState: SearchState = {
  loading: false,
  searchText: "",
  matchedWords: [],
  // @ts-ignore
  lastSearchRequest: null,
  lastSearchRequestCancelled: false,
};

export function searchReducer(
  state = initialState,
  action: SearchResultsAction
): SearchState {
  let a: SearchResultsAction;
  switch (action.type) {
    case SEARCH_UPDATE_LOADING:
      a = action as SearchUpdateLoadingAction;
      return { ...state, loading: a.payload };
    case SEARCH_UPDATE_TEXT:
      a = action as SearchUpdateTextAction;
      return { ...state, searchText: a.payload };
    case SEARCH_WORDS_RESULTS:
      a = action as SearchWordsResultsAction;
      return { ...state, matchedWords: a.payload };
    case SEARCH_UPDATE_REQUEST:
      a = action as SearchUpdateRequestAction;
      // cancel the last search request if there was one
      if (state.lastSearchRequest !== null) {
        state.lastSearchRequest.cancel();
        console.log("cancelling last request!");
      }
      return {
        ...state,
        lastSearchRequest: a.payload,
      };
    default:
      return state;
  }
}
