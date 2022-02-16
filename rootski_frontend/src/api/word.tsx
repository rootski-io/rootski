import { AxiosResponse } from "axios";
import axios from "axios";
import { RUSSIAN_API_URL } from "../config/constants";
import { Breakdown, WordData, WordType } from "../models/models";
import { doGetBreakdownRequest } from "./breakdown";
import { RootskiAPIError } from "./errors";

/**
 * Get word data from the backend API
 *
 * NOTE! This function ALWAYS calls doGetBreakdownRequest because the validation
 * logic for fetching the breakdown only happens
 *
 * @throws {RootskiAPIError} if the API call fails
 *     - if the status_code is 400, the breakdown was invalid; it likely did not sum to the word
 * @param word_id id of the word whose data is requested
 * @param word_type word type of the word with the associated ID (I can't remember if we need this
 *   but I don't want to double check right now :P)
 * @param authToken {string?} optional auth token to use for the API call
 * @returns
 */
export const doGetWordDataRequest = async (
  word_id: number,
  word_type: WordType,
  authToken?: string
): Promise<WordData> => {
  const getWordDataUrl = `${RUSSIAN_API_URL}/word/${word_id}/${word_type}`;

  // NOTE: the validateStatus object configures axios not to throw an error if it doesn't get 200
  // this way we can handle these error codes without a try/catch block
  const response: AxiosResponse = await axios.get(getWordDataUrl, {
    validateStatus: () => true,
  });
  if (response.status === 200) {
    // not sure why I have to parse this here, probably because
    // the backend isn't using Pydantic/FastAPI constructs for this
    // endpoint
    const wordData: WordData = response.data;
    const breakdown: Breakdown | null = await doGetBreakdownRequest(
      (word_id = word_id),
      (authToken = authToken)
    );

    // overwrite the breakdown given from /word endpoint with the
    // data from the /breakdown endpoint
    wordData.breakdown = breakdown;
    return wordData;
  } else {
    const error: RootskiAPIError = {
      status_code: response.status,
      message: `Got an an error with status code ${response.status} from the backend for word id "${word_id}" and word type "${word_type}": ${response.data}`,
    };
    throw error;
  }
};
