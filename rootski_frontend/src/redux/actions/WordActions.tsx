import { Dispatch } from "redux";
import {
  WORD_DATA_UPDATE_LOADING,
  WordPageLoadingAction,
  WordDataUpdateAction,
} from "./types";
import { WordType, WordData } from "../../models/models";
import { WORD_DATA_UPDATE } from "./types";
import { doGetWordDataRequest } from "../../api/word";

/**
 * Update redux store with whether the word data is still loading
 */
const updateLoading = function (loading: boolean): WordPageLoadingAction {
  return {
    type: WORD_DATA_UPDATE_LOADING,
    payload: loading,
  };
};

/**
 *  Update the redux store with the received payload with the word page data
 */
const updateWordData = function (
  wordData: WordData | null
): WordDataUpdateAction {
  return {
    type: WORD_DATA_UPDATE,
    payload: wordData,
  };
};

/**
 * Fetches all data associated with a word
 */
export const fetchWordDataAction = function (dispatch: Dispatch) {
  return async (
    word_id: number,
    word_type: WordType,
    authToken?: string
  ): Promise<void> => {
    // start loading
    dispatch(updateLoading(true));

    // clear out the existing word data
    dispatch(updateWordData(null));

    // perform GET /word/... request
    const wordData: WordData = await doGetWordDataRequest(
      (word_id = word_id),
      (word_type = word_type),
      (authToken = authToken)
    );

    console.log("got word data from server", wordData);

    dispatch(updateWordData(wordData));
    dispatch(updateLoading(false));
  };
};
