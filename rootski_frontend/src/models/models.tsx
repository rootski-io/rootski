export type WordType =
  | "noun"
  | "verb"
  | "adjective"
  | "pronoun"
  | "particle"
  | "adverb"
  | "conjunction"
  | null;

export interface Word {
  word: string;
  word_id: number;
  frequency: number;
  pos: WordType; // part of speech
}

export type MorphemeType = "root" | "prefix" | "suffix" | null;
export type MorphemeWordPOS = "any" | "adjective" | "noun" | "verb";

export interface Morpheme {
  morpheme_id: number | null; // id of morpheme in backend database; null if not an actual morpheme
  morpheme: string; // morpheme text
  position: number; // position of morpheme in word
  type: MorphemeType; // type of morpheme; null if not an actual morpheme
  word_pos: MorphemeWordPOS; // part of speech of morpheme
  meanings: Array<{ meaning: string }>; // descriptions of what the root means
  family_id?: number; // family which the morpheme is a member of
  level?: number; // level 1-6 of how common/difficult the root is; 6 is uncommon and/or difficult
  family?: string; // comma separated string of other morpheme variants in the family
}

export interface GroupedDefinitions {
  word_type: WordType;
  definitions: Array<Definition>;
}

export interface Definition {
  definition_id: number; // definition id in backend database
  def_position: number; // position of main definition
  sub_defs: Array<SubDefinition>;
}

export interface SubDefinition {
  sub_def_id: number; // definition id of the sub definition in the backend database
  sub_def_position: number; // position of the subdefinition with in the whole definition
  definition: string; // body of the definition
  notes: string | null; // extra notes (sometimes in russian) about the subdefinition; often not present
}

// Sentence showcasing a particular word
export interface ExampleSentence {
  eng: string; // english version of a sentence
  rus: string; // russian version of a sentence
  exact_match: 0 | 1; // whether the sentence contains exactly the word that is exemplified
}

export interface NounDeclensions {
  gender: "m" | "f" | "n";
  animate: 0 | 1;
  indeclinable: 0 | 1;
  nom: string;
  acc: string;
  prep: string;
  gen: string;
  dat: string;
  inst: string;
  nom_pl: string;
  acc_pl: string;
  prep_pl: string;
  gen_pl: string;
  dat_pl: string;
  inst_pl: string;
}

export interface AdjectiveForms {
  comp: string; // comparative form of the adjective
  fem_short: string;
  masc_short: string;
  neut_short: string;
  plural_short: string;
}

export interface AspectualPair {
  imp_word_id: number;
  imp_accent: string; // imperfective word with the accent
  pfv_word_id: number;
  pfv_accent: string;
}

export interface VerbConjugations {
  aspect: "perf" | "impf";
  "1st_per_sing": string;
  "2nd_per_sing": string;
  "3rd_per_sing": string;
  "1st_per_pl": string;
  "2nd_per_pl": string;
  "3rd_per_pl": string;
  past_m: string;
  past_f: string;
  past_n: string;
  past_pl: string;
  actv_part: string;
  pass_part: string;
  actv_past_part: string;
  pass_past_part: string;
  gerund: string;
  impr: string;
  impr_pl: string;
}

export interface Breakdown {
  is_verified: boolean;
  is_inference: boolean;
  submitted_by_current_user: boolean;
  date_submitted: Date;
  date_verified: Date | null;
  breakdown_items: Array<Morpheme>;
}

// super interface for entire word page
export interface WordData {
  word: Word;
  pos?: WordType;

  // breakdown: Array<Morpheme>;
  breakdown: Breakdown | null;
  definitions: Array<GroupedDefinitions>;
  sentences: Array<ExampleSentence>;
  // verb only
  conjugations?: VerbConjugations;
  aspectual_pairs?: Array<AspectualPair>;
  // noun only
  declensions?: NounDeclensions;
  // adjective only
  short_forms?: AdjectiveForms;
}
