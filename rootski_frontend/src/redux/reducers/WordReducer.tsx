import { WordData } from "../../models/models";
import {
  WordDataAction,
  WORD_DATA_UPDATE_LOADING,
  WORD_DATA_UPDATE,
  WordPageLoadingAction,
  WordDataUpdateAction,
} from "../actions/types";

export interface WordState {
  wordData: WordData | null;
  loading: boolean;
  loadingBreakdown: boolean;
}

const initialState: WordState = {
  wordData: null,
  loading: false,
  loadingBreakdown: false,
};

export function wordDataReducer(
  state = initialState,
  action: WordDataAction
): WordState {
  let a: WordDataAction;
  switch (action.type) {
    case WORD_DATA_UPDATE_LOADING:
      a = action as WordPageLoadingAction;
      return { ...state, loading: action.payload };
    case WORD_DATA_UPDATE:
      a = action as WordDataUpdateAction;
      return { ...state, wordData: action.payload };
    default:
      return state;
  }
}
