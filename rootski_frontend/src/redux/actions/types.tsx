import {
  Word,
  WordType,
  Morpheme,
  SubDefinition,
  ExampleSentence,
  VerbConjugations,
  AspectualPair,
  NounDeclensions,
  AdjectiveForms,
  WordData,
} from "../../models/models";
import axios from "axios";
import { CognitoIdToken } from "amazon-cognito-identity-js";
/**
 * This file contains constants for each Redux action type
 */

/**
 * Action types for SearchBar
 */
export const SEARCH_WORDS: string = "search_words";
export const SEARCH_WORDS_RESULTS: string = "search_words_results";
export const SEARCH_UPDATE_TEXT: string = "search_update_text";
export const SEARCH_UPDATE_LOADING: string = "search_update_loading";
export const SEARCH_UPDATE_USER_TYPING: string = "search_update_user_typing";
export const SEARCH_UPDATE_REQUEST: string = "search_set_request";

export interface SearchUpdateRequestAction {
  type: typeof SEARCH_UPDATE_REQUEST;
  payload: ReturnType<typeof axios.CancelToken.source> | null;
}

export interface SearchApiResponse {
  words: Array<Word>;
}

export interface SearchWordsResultsAction {
  type: typeof SEARCH_WORDS_RESULTS;
  payload: Array<Word>;
}

export interface SearchWordsAction {
  type: typeof SEARCH_WORDS;
  payload: string;
}

export interface SearchUpdateTextAction {
  type: typeof SEARCH_UPDATE_TEXT;
  payload: string;
}

export interface SearchUpdateLoadingAction {
  type: typeof SEARCH_UPDATE_LOADING;
  payload: boolean;
}

export interface SearchUpdateUserTypingAction {
  type: typeof SEARCH_UPDATE_USER_TYPING;
  payload: boolean;
}

export type SearchResultsAction =
  | SearchUpdateTextAction
  | SearchUpdateLoadingAction
  | SearchUpdateUserTypingAction
  | SearchWordsResultsAction
  | SearchUpdateRequestAction;

/*
 *  Action types for word page
 */
export const WORD_DATA_UPDATE_LOADING = "word_data_update_loading";
export const WORD_DATA_UPDATE = "word_data_update";

export interface WordPageLoadingAction {
  type: typeof WORD_DATA_UPDATE_LOADING;
  payload: boolean;
}

export interface WordDataUpdateAction {
  type: typeof WORD_DATA_UPDATE;
  payload: WordData | null;
}

export type WordDataAction = WordDataUpdateAction | WordPageLoadingAction;

/*
 * Morpheme Action Types
 */
export const SEARCH_MORPHEMES_RESULTS = "search_morphemes";

export interface SearchMorphemesAction {
  type: typeof SEARCH_MORPHEMES_RESULTS;
  payload: Array<Morpheme>;
}

/*
 * Auth Action Types
 */
export const LOGIN_USER = "login_user";
export const LOGOUT_USER = "logout_user";

export interface CognitoTokenPayload {
  at_hash: string;
  sub: string;
  email_verified: boolean;
  iss: string;
  "cognito:username": string;
  origin_jti: string;
  aud: string;
  event_id: string;
  token_use: string;
  auth_time: number;
  exp: number;
  iat: number;
  jti: string;
  email: string;
}

export interface LoginUserAction {
  type: typeof LOGIN_USER;
  payload: {
    idToken: string;
    idTokenPayload: CognitoTokenPayload;
  };
}

export interface LogoutUserAction {
  type: typeof LOGOUT_USER;
  payload: {
    idToken: null;
    idTokenPayload: null;
  };
}

export type AuthAction = LoginUserAction | LogoutUserAction;
