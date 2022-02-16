import axios, { AxiosRequestConfig } from "axios";
import { RUSSIAN_API_URL } from "../config/constants";
import {
  Breakdown,
  Morpheme,
  MorphemeType,
  MorphemeWordPOS,
} from "../models/models";
import { AxiosResponse } from "axios";
import { RootskiAPIError } from "./errors";

// ==============
// --- Models ---
// ==============

interface GetBreakdownSuccessResponse {
  word_id: number;
  word: string;
  is_verified: boolean;
  is_inference: boolean;
  submitted_by_current_user: boolean;
  date_submitted: string;
  date_verified: string | null;
  breakdown_items: Array<
    MorphemeBreakdownItemInResponse | NullMorphemeBreakdownItem
  >;
}

export interface SubmitBreakdownSuccessResponse {
  word_id: number;
  breakdown_id: number;
  is_verified: boolean;
}

interface NullMorphemeBreakdownItem {
  morpheme: string;
  position: number;
  morpheme_id: null;
}

interface MorphemeBreakdownItemInResponse {
  morpheme_id: number;
  position: number;
  type: MorphemeType;
  word_pos: MorphemeWordPOS;
  morpheme: string;
  family_id: number;
  family_meanings: Array<string>;
  level: number;
  family: string;
}

interface MorphemeBreakdownItemInRequest {
  position: number;
  morpheme_id: number;
}

// ========================
// --- Helper Functions ---
// ========================

/**
 * Transform a breakdown item from the response to fit the Morpheme model
 *
 * @param item one of the breakdown items in a successful GET /breakdown response
 * @returns Morpheme
 */
const getMorphemeFromBreakdownItem = (
  item: NullMorphemeBreakdownItem | MorphemeBreakdownItemInResponse
): Morpheme => {
  if (item.morpheme_id === null) {
    const null_item: NullMorphemeBreakdownItem = item;
    return {
      morpheme_id: null,
      morpheme: item.morpheme,
      position: item.position,
      level: -1,
      meanings: [],
      type: null,
      word_pos: "any",
    };
  } else {
    const morpheme_item: MorphemeBreakdownItemInResponse = item;
    return {
      morpheme_id: morpheme_item.morpheme_id,
      position: morpheme_item.position,
      type: morpheme_item.type,
      word_pos: morpheme_item.word_pos,
      morpheme: morpheme_item.morpheme,
      family_id: morpheme_item.family_id,
      meanings: morpheme_item.family_meanings.map((meaning: string) => {
        return { meaning };
      }),
      level: morpheme_item.level,
      family: morpheme_item.family,
    };
  }
};

const getBreakdownItemFromMorpheme = (
  morpheme: Morpheme
): MorphemeBreakdownItemInRequest | NullMorphemeBreakdownItem => {
  if (morpheme.morpheme_id === null) {
    const null_item: NullMorphemeBreakdownItem = {
      morpheme: morpheme.morpheme,
      position: morpheme.position,
      morpheme_id: null,
    };
    return null_item;
  } else {
    const morpheme_item: MorphemeBreakdownItemInRequest = {
      position: morpheme.position,
      morpheme_id: morpheme.morpheme_id,
    };
    return morpheme_item;
  }
};

// ============================
// --- API Client Functions ---
// ============================

/**
 * Request a word breakdown
 *
 * @throws an error if the response code is not 200 or 404
 * @param word_id of the word to whose breakdown is requested
 * @returns Array<Morpheme> if a breakdown was found for the request
 * @returns null if no breakdown was found, but the request was successful
 */
export const doGetBreakdownRequest = async (
  word_id: number,
  authToken?: string
): Promise<Breakdown | null> => {
  const getBreakdownUrl = `${RUSSIAN_API_URL}/breakdown/${word_id}`;

  // NOTE: the validateStatus object configures axios not to throw an error if it doesn't get 200
  // this way we can handle these error codes without a try/catch block
  const requestConfig: AxiosRequestConfig = {
    validateStatus: () => true,
  };
  if (typeof authToken === "string") {
    requestConfig.headers = {
      Authorization: `Bearer ${authToken}`,
      "Cache-Control": "no-cache",
    };
  }
  const response: AxiosResponse = await axios.get(
    getBreakdownUrl,
    requestConfig
  );
  if (response.status === 200) {
    const successResponse: GetBreakdownSuccessResponse = response.data;
    const breakdown_items: Array<Morpheme> =
      successResponse.breakdown_items.map(getMorphemeFromBreakdownItem);
    return {
      ...successResponse,
      breakdown_items: breakdown_items,
      date_submitted: new Date(successResponse.date_submitted),
      date_verified: successResponse.date_verified
        ? new Date(successResponse.date_verified)
        : null,
    };
  } else if (response.status == 404) {
    return null;
  } else {
    throw Error(
      `Got an an error with status code ${response.status} from the backend for word id "${word_id}": ${response.data}`
    );
  }
};

/**
 * @throws {RootskiAPIError} if the response code is not 200
 *      - if the status_code is 400, the breakdown is invalid; likely the morphemes did not sum to the word
 * @param word_id id of the word the breakdown is for
 * @param breakdown_items morphemes which should sum to the word with the corresponding word_id
 * @param authToken Cognito JWT token
 * @returns
 */
export const doSubmitBreakdownRequest = async (
  word_id: number,
  breakdown_items: Array<
    NullMorphemeBreakdownItem | MorphemeBreakdownItemInRequest
  >,
  authToken: string
): Promise<SubmitBreakdownSuccessResponse> => {
  const submitBreakdownUrl = `${RUSSIAN_API_URL}/breakdown`;
  const payload = { word_id, breakdown_items };
  // NOTE: the validateStatus object configures axios not to throw an error if it doesn't get 200
  // this way we can handle these error codes without a try/catch block
  const response: AxiosResponse = await axios.post(
    submitBreakdownUrl,
    payload,
    {
      validateStatus: () => true,
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    }
  );
  if (response.status === 200) {
    const successResponse: SubmitBreakdownSuccessResponse = response.data;
    return successResponse;
  } else if (response.status === 400) {
    const error: RootskiAPIError = {
      status_code: response.status,
      message: response.data.message,
    };
    throw error;
  } else {
    const error: RootskiAPIError = {
      status_code: response.status,
      message: `
                Got an an error with status code ${response.status} from the backend
                when submitting a breakdown with payload ${payload}: ${response}
          `,
    };
    throw error;
  }
};

/**
 * Wrapper around doSubmitBreakdownRequest for easy use
 * with an array of Morphemes. See the above docstring for
 * @returns and @throws statements.
 *
 * @param morphemes morphemes comprising the breakdown being submitted
 *
 * other params are the same as the above function
 */
export const doSubmitBreakdownRequestWithMorphemes = async (
  word_id: number,
  morphemes: Array<Morpheme>,
  authToken: string
): Promise<SubmitBreakdownSuccessResponse> => {
  const breakdown_items = morphemes.map(getBreakdownItemFromMorpheme);
  return await doSubmitBreakdownRequest(word_id, breakdown_items, authToken);
};
