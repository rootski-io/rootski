import { RUSSIAN_API_URL } from "../config/constants";
import { AxiosResponse } from "axios";
import axios from "axios";
import { Morpheme } from "../models/models";
import { RootskiAPIError } from "./errors";

export interface MorphemeIndex {
  [key: number]: Morpheme;
}

/**
 * Request the MorphemeIndex from the API. This is used to cache all of the
 * morphemes in Rootski locally so that there is no latency while breaking down words.
 *
 * @returns an object containing all of the morphemes
 * @throws {RootskiAPIError} if the request fails for any reason
 */
export const doGetMorphemesJsonRequest = async (): Promise<MorphemeIndex> => {
  const getAllMorphemesUrl = `${RUSSIAN_API_URL}/morpheme/morphemes.json`;
  const response: AxiosResponse = await axios.get(getAllMorphemesUrl);
  if (response.status === 200) {
    const morphemeIndex: MorphemeIndex = response.data;
    return morphemeIndex;
  } else {
    const error: RootskiAPIError = {
      status_code: response.status,
      message: `Error when requesting morphemes.json, got this response from the API ${response.data}`,
    };
    throw error;
  }
};
