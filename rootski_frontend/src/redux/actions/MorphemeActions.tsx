import { SearchMorphemesAction, SEARCH_MORPHEMES_RESULTS } from "./types";
import { Morpheme } from "../../models/models";
import { doGetMorphemesJsonRequest, MorphemeIndex } from "../../api/morpheme";

let MORPHEMES_SINGLETON: MorphemeIndex;

/**
 * Fetch the morpheme index from the backend
 */
const initMorphemesSingleton = async (): Promise<void> => {
  if (MORPHEMES_SINGLETON === undefined) {
    MORPHEMES_SINGLETON = await doGetMorphemesJsonRequest();
  }
};
initMorphemesSingleton();

const updateMorphemes = (
  morphemeResults: Array<Morpheme>
): SearchMorphemesAction => {
  return { type: SEARCH_MORPHEMES_RESULTS, payload: morphemeResults };
};

export const searchMorphemes = (
  searchKey: string
): {
  exactMatches: Array<Morpheme>;
  similarMatches: Array<Morpheme>;
} => {
  if (!searchKey) {
    // return no results if search key is invalid
    return {
      exactMatches: [],
      similarMatches: [],
    };
  }

  // prepare to search for morphemes matching exactly with :searchKey: and containing :searchKey:
  const exactMatches: Array<Morpheme> = [];
  const similarMatches: Array<Morpheme> = [];

  for (const morpheme_id in MORPHEMES_SINGLETON) {
    const morpheme: Morpheme = { ...MORPHEMES_SINGLETON[morpheme_id] };
    if (morpheme.morpheme === searchKey.toLowerCase()) {
      exactMatches.push(morpheme);
    } else if (morpheme.morpheme.includes(searchKey.toLowerCase())) {
      similarMatches.push(morpheme);
    }
  }
  return {
    exactMatches: exactMatches,
    similarMatches: similarMatches,
  };
};
