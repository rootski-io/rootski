export const PREFIX_OPAQUE = "#38C172";
export const SUFFIX_OPAQUE = "#3183C8";
export const ROOT_OPAQUE = "#E46464";

export const PREFIX_TRANSPARENT = PREFIX_OPAQUE + "1f";
export const SUFFIX_TRANSPARENT = SUFFIX_OPAQUE + "1f";
export const ROOT_TRANSPARENT = ROOT_OPAQUE + "1f";

// these dictionaries allow you to get the color with dict[morpheme.type]
export const MORPHEME_COLORS = {
  prefix: PREFIX_OPAQUE,
  root: ROOT_OPAQUE,
  suffix: SUFFIX_OPAQUE,
  link: "",
  none: "",
};
export const MORPHEME_COLORS_TRANSPARENT = {
  prefix: PREFIX_TRANSPARENT,
  root: ROOT_TRANSPARENT,
  suffix: SUFFIX_TRANSPARENT,
  link: "",
  none: "",
};
